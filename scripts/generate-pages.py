#!/usr/bin/env python3
"""Generate the page shells under api/ from scripts/apis-data.json.

Each shell carries the page's title and metadata plus the page data embedded as
JSON; the content is rendered by the React entries in src/entries/ using
Sundsvall's design system (@sk-web-gui/react + @sk-web-gui/core). The data file
holds facts derived from each api-service source repository (see CLAUDE.md for
the method). The start page needs no generation step: src/pages/IndexPage.tsx
imports apis-data.json directly.

Run from anywhere: python3 scripts/generate-pages.py
"""

import html
import json
import os
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "scripts", "apis-data.json")
OUT = os.path.join(ROOT, "api")


def has_spec(api):
    return os.path.exists(os.path.join(ROOT, "assets", "openapi", f"{api['slug']}.yml"))


def sbom_path(api):
    return os.path.join(ROOT, "assets", "sbom", f"{api['slug']}.spdx.json")


def has_sbom(api):
    return os.path.exists(sbom_path(api))


def load_sbom(api):
    """Return (components, licence counts, provenance) from the SPDX document.

    Components are the packages carrying a package-manager purl; the two
    remaining packages describe the scanned repository itself.
    """
    with open(sbom_path(api), encoding="utf-8") as f:
        doc = json.load(f)
    components = []
    for pkg in doc.get("packages", []):
        if not pkg.get("externalRefs"):
            continue
        # licenseConcluded first: normalize-sbom.py records manually verified
        # licences there (see scripts/license-overrides.json), while
        # licenseDeclared honestly keeps what the package metadata itself says.
        licens = next(
            (v for v in (pkg.get("licenseConcluded"), pkg.get("licenseDeclared"))
             if v and v not in ("NOASSERTION", "NONE")),
            "Ej angiven",
        )
        components.append({
            "namn": pkg.get("name", ""),
            "version": pkg.get("versionInfo", ""),
            "licens": licens,
        })
    # Multi-module repositories (api-service-operaton has 12 poms) list the same
    # dependency once per module -- 6895 entries for 331 distinct components. The
    # SPDX document keeps them all, since the relationships reference them, but the
    # page shows each component once.
    unique = {(c["namn"], c["version"], c["licens"]): c for c in components}
    components = sorted(unique.values(), key=lambda c: (c["namn"].lower(), c["version"]))
    licenser = Counter(c["licens"] for c in components)
    provenans = {
        "namn": doc.get("name", ""),
        "created": doc.get("creationInfo", {}).get("created", ""),
        "spdx": doc.get("spdxVersion", ""),
        "verktyg": next(
            (c[len("Tool: "):] for c in doc.get("creationInfo", {}).get("creators", [])
             if c.startswith("Tool: ")),
            "",
        ),
    }
    return components, licenser, provenans


def shell(title, description, entry, data):
    """Render one page shell: head metadata, embedded page data, React entry."""
    # "</" must not appear verbatim inside a script element.
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title, quote=False)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
  <link rel="apple-touch-icon" href="../assets/favicon-180.png">
</head>
<body>
  <script type="application/json" id="page-data">{payload}</script>
  <div id="root"></div>
  <script type="module" src="/src/entries/{entry}.tsx"></script>
</body>
</html>
"""


def api_shell(api):
    sbom_summary = None
    if has_sbom(api):
        komponenter, licenser, _ = load_sbom(api)
        sbom_summary = {"komponenter": len(komponenter), "licenser": len(licenser)}
    return shell(
        f"{api['namn']} – API-katalogen",
        api.get("ingress", ""),
        "api",
        {
            "api": api,
            "hasSpec": has_spec(api),
            "hasSbom": has_sbom(api),
            "sbom": sbom_summary,
        },
    )


def swagger_shell(api):
    return shell(
        f"{api['namn']} – Swagger UI – API-katalogen",
        f"Interaktiv API-dokumentation (Swagger UI) för {api['namn']}.",
        "swagger",
        {
            "api": {
                "slug": api["slug"],
                "namn": api["namn"],
                "kategori": api["kategori"],
                "apiVersion": api.get("apiVersion"),
            }
        },
    )


def sbom_shell(api):
    komponenter, licenser, provenans = load_sbom(api)
    return shell(
        f"{api['namn']} – Programvaruförteckning (SBOM) – API-katalogen",
        f"Programvaruförteckning (SBOM) i SPDX-format för {api['namn']}: "
        "tredjepartskomponenter med version och licens.",
        "sbom",
        {
            "api": {
                "slug": api["slug"],
                "namn": api["namn"],
                "kategori": api["kategori"],
                "repo": api["repo"],
            },
            "komponenter": komponenter,
            "licenser": sorted(licenser.items(), key=lambda x: (-x[1], x[0].lower())),
            "provenans": provenans,
        },
    )


def main():
    with open(DATA, encoding="utf-8") as f:
        apis = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    missing = []
    missing_sbom = []
    for api in apis:
        with open(os.path.join(OUT, f"{api['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(api_shell(api))
        if has_spec(api):
            with open(os.path.join(OUT, f"{api['slug']}-swagger.html"), "w", encoding="utf-8") as f:
                f.write(swagger_shell(api))
        else:
            missing.append(api["slug"])
        if has_sbom(api):
            with open(os.path.join(OUT, f"{api['slug']}-sbom.html"), "w", encoding="utf-8") as f:
                f.write(sbom_shell(api))
        else:
            missing_sbom.append(api["slug"])
    print(f"wrote {len(apis)} API page shells ({len(apis) - len(missing)} Swagger UI pages, "
          f"{len(apis) - len(missing_sbom)} SBOM pages)")
    if missing:
        print("no OpenAPI spec (Swagger UI skipped):", ", ".join(missing))
    if missing_sbom:
        print("no SBOM (SBOM page skipped):", ", ".join(missing_sbom))


if __name__ == "__main__":
    main()
