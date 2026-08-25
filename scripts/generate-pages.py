#!/usr/bin/env python3
"""Generate API pages, Swagger UI pages and start-page cards from scripts/apis-data.json.

Everything in api/ is generated from the data file, which holds facts derived
from each api-service source repository (see CLAUDE.md for the method).

Run from anywhere: python3 scripts/generate-pages.py
"""

import html
import json
import os
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "scripts", "apis-data.json")
OUT = os.path.join(ROOT, "api")

SWAGGER_UI_VERSION = "5.17.14"  # vendored in assets/vendor/swagger-ui/

CATEGORY_ORDER = [
    "Kommunikation",
    "Ärendehantering",
    "Ekonomi och fakturering",
    "Dokument och arkiv",
    "Parts- och kunddata",
    "AI-tjänster",
    "Integration",
    "Samhällsservice",
    "Utbildning",
    "Utvecklingsverktyg",
]

STATUS_LABEL = {"poc": "Prototyp", "avvecklad": "Avvecklad", "verktyg": "Verktyg"}


def e(s):
    return html.escape(str(s), quote=False)


def header(depth):
    p = "../" * depth
    return f"""<header class="site-header">
  <div class="container header-inner">
    <div class="brand">
      <span class="brand-mark" aria-hidden="true">⬡</span>
      <a class="brand-name" href="{p}index.html">API-katalogen</a>
    </div>
    <nav class="site-nav" aria-label="Huvudmeny">
      <a href="{p}index.html#om-katalogen">Om katalogen</a>
      <a href="{p}index.html#apier">API:er</a>
      <a href="https://github.com/Sundsvallskommun" rel="external">GitHub</a>
    </nav>
  </div>
</header>"""


def footer():
    return """<footer class="site-footer">
  <div class="container footer-inner">
    <div>
      <p class="footer-title">API-katalogen</p>
      <p>En översikt över de API:er som körs i produktion på Sundsvalls kommuns API-plattform.</p>
    </div>
    <div>
      <p class="footer-title">Länkar</p>
      <ul class="footer-links">
        <li><a href="https://github.com/Sundsvallskommun" rel="external">Sundsvalls kommun på GitHub</a></li>
        <li><a href="https://sundsvall.se" rel="external">sundsvall.se</a></li>
      </ul>
    </div>
  </div>
</footer>"""


def status_tag(api):
    label = STATUS_LABEL.get(api.get("status"))
    if not label:
        return ""
    return f' <span class="app-tag app-tag-light app-tag-status">{e(label)}</span>'


def status_tag_card(api):
    label = STATUS_LABEL.get(api.get("status"))
    if not label:
        return ""
    return f' <span class="app-tag app-tag-status">{e(label)}</span>'


def dependency_rows(api):
    rows = []
    for d in api.get("beroenden") or []:
        ver = e(d.get("version") or "–")
        rows.append(f"            <tr><td>{e(d['name'])}</td><td>{ver}</td><td>{e(d.get('usage') or '')}</td></tr>")
    return "\n".join(rows)


def arch_prose(api):
    t = api.get("teknik") or {}
    bits = []
    stack = ", ".join(x for x in [t.get("sprak"), t.get("ramverk")] if x)
    if stack:
        bits.append(f"API:et är en mikrotjänst ({stack}).")
    else:
        bits.append("API:et är en mikrotjänst; se källkoden för detaljer om uppbyggnaden.")
    bits.append("Konsumenter når tjänsten via kommunens gemensamma API-plattform (WSO2) på api.sundsvall.se – tjänsten anropas aldrig direkt.")
    if api.get("beroenden"):
        bits.append("Tjänsten anropar i sin tur andra mikrotjänster i kommunens tjänstelandskap.")
    if api.get("databas"):
        bits.append(f"Lagring: {e(api['databas'])}.")
    integ = api.get("integrationer") or []
    if integ:
        bits.append("Övriga integrationer som förekommer i koden: " + e(", ".join(integ)) + ".")
    return " ".join(bits)


def tech_list(api):
    t = api.get("teknik") or {}
    items = []
    if t.get("sprak"):
        items.append(f"<li><strong>Språk:</strong> {e(t['sprak'])}</li>")
    if t.get("ramverk"):
        items.append(f"<li><strong>Ramverk:</strong> {e(t['ramverk'])}</li>")
    if api.get("databas"):
        items.append(f"<li><strong>Databas:</strong> {e(api['databas'])}</li>")
    if t.get("ovrigt"):
        items.append(f"<li><strong>Övrigt:</strong> {e(t['ovrigt'])}</li>")
    if not items:
        items.append("<li>Se källkodens byggfiler för detaljer.</li>")
    return "\n        ".join(items)


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
        licens = pkg.get("licenseDeclared") or "NOASSERTION"
        if licens == "NOASSERTION":
            licens = "Ej angiven"
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


def page(api):
    slug = api["slug"]
    namn = api["namn"]
    repo_url = f"https://github.com/Sundsvallskommun/{api['repo']}"
    funktioner = "\n".join(
        f'            <li><strong>{e(f["titel"])}</strong> – {e(f["text"])}</li>'
        for f in (api.get("funktioner") or [])
    )
    beskrivning = "\n".join(f"          <p>\n            {e(p)}\n          </p>" for p in api.get("beskrivning", []))
    anteckningar = api.get("anteckningar") or []
    notes_html = ""
    if anteckningar:
        notes_html = ("\n      <h3>Noterbart ur källkoden</h3>\n      <ul>\n"
                      + "\n".join(f"        <li>{e(n)}</li>" for n in anteckningar) + "\n      </ul>")
    beroenden = api.get("beroenden") or []
    if beroenden:
        dep_html = f"""      <h3>Beroenden till andra mikrotjänster</h3>
      <p>
        Tjänsten anropar följande mikrotjänster. Versionerna är hämtade ur
        källkodens integrationsklienter.
      </p>
      <div class="table-wrap">
        <table>
          <caption class="sr-only">Mikrotjänster som {e(namn)} anropar</caption>
          <thead>
            <tr><th scope="col">Tjänst</th><th scope="col">Version</th><th scope="col">Användning</th></tr>
          </thead>
          <tbody>
{dependency_rows(api)}
          </tbody>
        </table>
      </div>"""
    else:
        dep_html = """      <h3>Beroenden till andra mikrotjänster</h3>
      <p>
        Inga anrop till andra mikrotjänster hittades i källkodens konfiguration.
      </p>"""
    konf = api.get("konfiguration") or []
    konf_html = "\n".join(f"        <li>{e(k)}</li>" for k in konf) or "        <li>Se källkodens miljöfilsexempel.</li>"

    # The button row is shared: an API without an OpenAPI specification still has
    # a software bill of materials, and vice versa. Kept as pre-wrapped lines so the
    # generated HTML stays wrapped the way the rest of the page is.
    if has_spec(api):
        intro_lines = [
            "        API:ets samtliga resurser, parametrar och datamodeller finns beskrivna i en",
            "        OpenAPI-specifikation som är hämtad ur källkodsförrådet. Den kan utforskas",
            "        interaktivt i Swagger UI eller laddas ner som YAML.",
        ]
    else:
        intro_lines = [
            "        Ingen incheckad OpenAPI-specifikation hittades i källkodsförrådet; se",
            "        källkoden för aktuell API-dokumentation.",
        ]
    if has_sbom(api):
        intro_lines += [
            "        Programvaruförteckningen (SBOM) listar tjänstens samtliga",
            "        tredjepartskomponenter med version och licens.",
        ]
    apidok_intro = "\n".join(intro_lines)

    buttons = []
    swagger_fact_link = ""
    if has_spec(api):
        buttons.append(f'        <a class="button button-primary" href="{slug}-swagger.html">Öppna Swagger UI</a>')
        buttons.append(f'        <a class="button button-outline" href="../assets/openapi/{slug}.yml" download>OpenAPI-specifikation (YAML)</a>')
        swagger_fact_link = f"""          <p class="fact-box-link">
            <a href="{slug}-swagger.html">API-dokumentation (Swagger UI)</a>
          </p>
"""
    sbom_fact_link = ""
    if has_sbom(api):
        buttons.append(f'        <a class="button button-outline" href="{slug}-sbom.html">Programvaruförteckning (SBOM)</a>')
        sbom_fact_link = f"""          <p class="fact-box-link">
            <a href="{slug}-sbom.html">Programvaruförteckning (SBOM)</a>
          </p>
"""

    sbom_section = ""
    if has_sbom(api):
        komponenter, licenser, _ = load_sbom(api)
        sbom_section = f"""
      <h3>Programvaruförteckning</h3>
      <p>
        Tjänsten bygger på {len(komponenter)} tredjepartskomponenter fördelade på
        {len(licenser)} olika licenser. Till skillnad från tabellen ovan, som listar
        andra mikrotjänster, avses här de programbibliotek som ingår i bygget.
        Se <a href="{slug}-sbom.html">programvaruförteckningen</a> för hela listan.
      </p>
"""

    actions = ""
    if buttons:
        actions = '      <div class="hero-actions">\n' + "\n".join(buttons) + "\n      </div>\n"
    apidok_section = f"""
  <section class="section section-slim" id="api-dokumentation">
    <div class="container">
      <h2>API-dokumentation</h2>
      <p class="section-intro">
{apidok_intro}
      </p>
{actions}    </div>
  </section>
"""

    return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(namn)} – API-katalogen</title>
  <meta name="description" content="{html.escape(api.get('ingress', ''), quote=True)}">
  <link rel="stylesheet" href="../assets/styles.css">
  <link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
  <link rel="apple-touch-icon" href="../assets/favicon-180.png">
</head>
<body>

{header(1)}

<main>

  <section class="page-hero">
    <div class="container">
      <nav class="breadcrumb" aria-label="Brödsmulor">
        <a href="../index.html">Start</a> <span aria-hidden="true">/</span>
        <a href="../index.html#apier">API:er</a> <span aria-hidden="true">/</span>
        <span aria-current="page">{e(namn)}</span>
      </nav>
      <span class="app-tag app-tag-light">{e(api['kategori'])}</span>{status_tag(api)}
      <h1>{e(namn)}</h1>
      <p class="hero-lead">
        {e(api.get('ingress', ''))}
      </p>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Om API:et</h2>
      <div class="columns">
        <div class="column-text">
{beskrivning}

          <h3>Det här gör API:et</h3>
          <ul class="app-modules">
{funktioner}
          </ul>
        </div>
        <aside class="fact-box" aria-label="Snabbfakta">
          <h3>Snabbfakta</h3>
          <ul>
            <li>Version: <strong>{e(api.get('apiVersion', '–'))}</strong></li>
            <li>Kategori: <strong>{e(api['kategori'])}</strong></li>
            <li>Status: <strong>{e(STATUS_LABEL.get(api.get('status'), 'Aktiv'))}</strong></li>
            <li>Målgrupp: <strong>{e(api.get('malgrupp', '–'))}</strong></li>
          </ul>
{swagger_fact_link}{sbom_fact_link}          <p class="fact-box-link">
            <a href="{repo_url}" rel="external">Källkod på GitHub</a>
          </p>
        </aside>
      </div>
    </div>
  </section>
{apidok_section}
  <section class="section section-alt" id="teknisk-dokumentation">
    <div class="container">
      <h2>Teknisk dokumentation</h2>
      <p class="section-intro">
        Nedan beskrivs hur tjänsten är uppbyggd, vilka andra tjänster den anropar och
        vad som krävs för att driftsätta den. Informationen är härledd ur källkoden
        och dess konfiguration på GitHub.
      </p>

      <h3>Arkitektur</h3>
      <figure class="diagram">
        <div class="diagram-wrap">
          <img src="../assets/diagrams/{slug}.svg" alt="Arkitekturskiss för {e(namn)}: tjänstens delar och dess integrationer.">
        </div>
        <figcaption>Lösningsarkitektur, härledd ur källkodens konfiguration.</figcaption>
      </figure>
      <p>
        {arch_prose(api)}
      </p>

      <h3>Teknikstack</h3>
      <ul>
        {tech_list(api)}
      </ul>

{dep_html}
{sbom_section}
      <h3>Konfiguration och driftsättning</h3>
      <ul>
{konf_html}
      </ul>{notes_html}

      <h3>Källkod</h3>
      <p>
        Källkoden är öppen och finns hos
        <a href="{repo_url}" rel="external">Sundsvalls kommun på GitHub</a>.
        I källkodsförrådet finns även instruktioner för att klona, konfigurera och
        starta tjänsten i egen miljö.
      </p>
    </div>
  </section>

</main>

{footer()}

</body>
</html>
"""


def swagger_page(api):
    slug = api["slug"]
    namn = api["namn"]
    return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(namn)} – Swagger UI – API-katalogen</title>
  <meta name="description" content="Interaktiv API-dokumentation (Swagger UI) för {e(namn)}.">
  <link rel="stylesheet" href="../assets/vendor/swagger-ui/swagger-ui.css">
  <link rel="stylesheet" href="../assets/styles.css">
  <link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
  <link rel="apple-touch-icon" href="../assets/favicon-180.png">
</head>
<body>

{header(1)}

<main>

  <section class="page-hero page-hero-slim">
    <div class="container">
      <nav class="breadcrumb" aria-label="Brödsmulor">
        <a href="../index.html">Start</a> <span aria-hidden="true">/</span>
        <a href="../index.html#apier">API:er</a> <span aria-hidden="true">/</span>
        <a href="{slug}.html">{e(namn)}</a> <span aria-hidden="true">/</span>
        <span aria-current="page">Swagger UI</span>
      </nav>
      <span class="app-tag app-tag-light">{e(api['kategori'])}</span>
      <h1>{e(namn)} {e(api.get('apiVersion', ''))}</h1>
      <p class="hero-lead">
        Interaktiv API-dokumentation, genererad ur tjänstens OpenAPI-specifikation.
        Anrop i produktion görs via kommunens API-plattform på api.sundsvall.se.
      </p>
    </div>
  </section>

  <section class="section swagger-section">
    <div class="container">
      <div id="swagger-ui" aria-label="Swagger UI för {e(namn)}"></div>
      <noscript>
        <p>
          Swagger UI kräver JavaScript. Specifikationen kan i stället läsas som
          <a href="../assets/openapi/{slug}.yml">YAML</a>.
        </p>
      </noscript>
    </div>
  </section>

</main>

{footer()}

<script src="../assets/vendor/swagger-ui/swagger-ui-bundle.js"></script>
<script>
  window.addEventListener('load', function () {{
    window.ui = SwaggerUIBundle({{
      url: '../assets/openapi/{slug}.yml',
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis],
      layout: 'BaseLayout',
      docExpansion: 'list',
      defaultModelsExpandDepth: 0,
      validatorUrl: null,
      tryItOutEnabled: false,
      supportedSubmitMethods: []
    }});
  }});
</script>

</body>
</html>
"""


def sbom_page(api):
    slug = api["slug"]
    namn = api["namn"]
    repo_url = f"https://github.com/Sundsvallskommun/{api['repo']}"
    komponenter, licenser, prov = load_sbom(api)

    licens_rader = "\n".join(
        f"            <tr><td>{e(licens)}</td><td>{antal}</td></tr>"
        for licens, antal in sorted(licenser.items(), key=lambda x: (-x[1], x[0].lower()))
    )
    komponent_rader = "\n".join(
        f'            <tr><td>{e(k["namn"])}</td><td>{e(k["version"])}</td><td>{e(k["licens"])}</td></tr>'
        for k in komponenter
    )
    datum = prov["created"][:10]

    return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(namn)} – Programvaruförteckning (SBOM) – API-katalogen</title>
  <meta name="description" content="Programvaruförteckning (SBOM) i SPDX-format för {e(namn)}: tredjepartskomponenter med version och licens.">
  <link rel="stylesheet" href="../assets/styles.css">
  <link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
  <link rel="apple-touch-icon" href="../assets/favicon-180.png">
</head>
<body>

{header(1)}

<main>

  <section class="page-hero page-hero-slim">
    <div class="container">
      <nav class="breadcrumb" aria-label="Brödsmulor">
        <a href="../index.html">Start</a> <span aria-hidden="true">/</span>
        <a href="../index.html#apier">API:er</a> <span aria-hidden="true">/</span>
        <a href="{slug}.html">{e(namn)}</a> <span aria-hidden="true">/</span>
        <span aria-current="page">SBOM</span>
      </nav>
      <span class="app-tag app-tag-light">{e(api['kategori'])}</span>
      <h1>{e(namn)} – programvaruförteckning</h1>
      <p class="hero-lead">
        Samtliga tredjepartskomponenter som ingår i tjänstens bygge, med version och
        licens. Förteckningen är maskinellt härledd ur källkodens beroendeträd och
        publiceras i SPDX-format.
      </p>
      <div class="hero-actions">
        <a class="button button-primary" href="../assets/sbom/{slug}.spdx.json" download>Ladda ner SPDX (JSON)</a>
        <a class="button button-secondary" href="{slug}.html">Tillbaka till {e(namn)}</a>
      </div>
    </div>
  </section>

  <section class="section section-slim" id="om-forteckningen">
    <div class="container">
      <h2>Om förteckningen</h2>
      <ul>
        <li>Antal komponenter: <strong>{len(komponenter)}</strong></li>
        <li>Antal unika licenser: <strong>{len(licenser)}</strong></li>
        <li>Källa: <strong>{e(prov['namn'])}</strong> (<a href="{repo_url}" rel="external">källkod på GitHub</a>)</li>
        <li>Avser källkod från: <strong>{e(datum)}</strong></li>
        <li>Format: <strong>{e(prov['spdx'])}</strong>, genererad med <strong>{e(prov['verktyg'])}</strong></li>
      </ul>
      <p>
        Förteckningen uppdateras automatiskt och beskriver beroendena i tjänstens
        huvudgren vid angivet datum. Den avser programbibliotek – vilka andra
        mikrotjänster API:et anropar framgår av
        <a href="{slug}.html#teknisk-dokumentation">den tekniska dokumentationen</a>.
      </p>
    </div>
  </section>

  <section class="section section-alt" id="licenser">
    <div class="container">
      <h2>Licenser</h2>
      <p class="section-intro">
        Fördelning av deklarerade licenser bland komponenterna.
      </p>
      <div class="table-wrap">
        <table>
          <caption class="sr-only">Licensfördelning för {e(namn)}</caption>
          <thead>
            <tr><th scope="col">Licens</th><th scope="col">Antal komponenter</th></tr>
          </thead>
          <tbody>
{licens_rader}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="section" id="komponenter">
    <div class="container">
      <h2>Komponenter</h2>
      <p class="section-intro">
        Samtliga {len(komponenter)} komponenter, inklusive transitiva beroenden.
      </p>
      <p class="sbom-filter" hidden>
        <label for="sbom-filter">Filtrera listan</label>
        <input type="search" id="sbom-filter" placeholder="Sök på komponent eller licens" autocomplete="off">
        <span id="sbom-count" aria-live="polite"></span>
      </p>
      <div class="table-wrap">
        <table id="sbom-table">
          <caption class="sr-only">Tredjepartskomponenter i {e(namn)}</caption>
          <thead>
            <tr><th scope="col">Komponent</th><th scope="col">Version</th><th scope="col">Licens</th></tr>
          </thead>
          <tbody>
{komponent_rader}
          </tbody>
        </table>
      </div>
    </div>
  </section>

</main>

{footer()}

<script>
  // Progressive enhancement: the table is fully rendered server-side and stays
  // usable without JavaScript.
  (function () {{
    var input = document.getElementById('sbom-filter');
    var count = document.getElementById('sbom-count');
    var rows = Array.prototype.slice.call(
      document.querySelectorAll('#sbom-table tbody tr')
    );
    if (!input || !rows.length) return;
    document.querySelector('.sbom-filter').hidden = false;
    input.addEventListener('input', function () {{
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (row) {{
        var match = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
        row.hidden = !match;
        if (match) shown++;
      }});
      count.textContent = q ? shown + ' av ' + rows.length : '';
    }});
  }})();
</script>

</body>
</html>
"""


def teaser_card(api):
    href = f"api/{api['slug']}.html"
    return f"""        <a class="teaser-card" href="{href}">
          <span class="app-tag">{e(api['kategori'])}</span>{status_tag_card(api)}
          <h3>{e(api['namn'])}</h3>
          <p>
            {e(api.get('ingress', ''))}
          </p>
          <span class="teaser-more">Läs mer →</span>
        </a>"""


def build_cards(apis):
    by_cat = {}
    for api in apis:
        by_cat.setdefault(api["kategori"], []).append(api)
    blocks = []
    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        cards = "\n\n".join(
            teaser_card(api) for api in sorted(by_cat[cat], key=lambda a: a["namn"].lower())
        )
        blocks.append(f'      <h3 class="card-group-title">{e(cat)}</h3>\n      <div class="card-grid">\n\n{cards}\n\n      </div>')
    return "\n\n".join(blocks)


def main():
    with open(DATA, encoding="utf-8") as f:
        apis = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    missing = []
    missing_sbom = []
    for api in apis:
        with open(os.path.join(OUT, f"{api['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(page(api))
        if has_spec(api):
            with open(os.path.join(OUT, f"{api['slug']}-swagger.html"), "w", encoding="utf-8") as f:
                f.write(swagger_page(api))
        else:
            missing.append(api["slug"])
        if has_sbom(api):
            with open(os.path.join(OUT, f"{api['slug']}-sbom.html"), "w", encoding="utf-8") as f:
                f.write(sbom_page(api))
        else:
            missing_sbom.append(api["slug"])
    print(f"wrote {len(apis)} API pages ({len(apis) - len(missing)} Swagger UI pages, "
          f"{len(apis) - len(missing_sbom)} SBOM pages)")
    if missing:
        print("no OpenAPI spec (Swagger UI skipped):", ", ".join(missing))
    if missing_sbom:
        print("no SBOM (SBOM page skipped):", ", ".join(missing_sbom))

    index_path = os.path.join(ROOT, "index.html")
    with open(index_path, encoding="utf-8") as f:
        idx = f.read()
    begin, end = "<!-- BEGIN:API-CARDS -->", "<!-- END:API-CARDS -->"
    if begin not in idx or end not in idx:
        raise SystemExit("index.html saknar API-CARDS-markörer")
    new = idx[: idx.index(begin) + len(begin)] + "\n" + build_cards(apis) + "\n      " + idx[idx.index(end):]
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new)
    print("updated index.html cards")


if __name__ == "__main__":
    main()
