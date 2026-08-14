#!/usr/bin/env python3
"""Generate API pages, Swagger UI pages and start-page cards from scripts/apis-data.json.

Everything in api/ is generated from the data file, which holds facts derived
from each api-service source repository (see CLAUDE.md for the method).

Run from anywhere: python3 scripts/generate-pages.py
"""

import html
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "scripts", "apis-data.json")
OUT = os.path.join(ROOT, "api")

SWAGGER_UI_VERSION = "5.17.14"  # vendored in assets/vendor/swagger-ui/

CATEGORY_ORDER = [
    "Kommunikation",
    "Ärendehantering",
    "Master-data",
    "Ekonomi",
    "Integration",
    "AI-tjänster",
    "Övrigt",
]

STATUS_LABEL = {"poc": "Prototyp", "avvecklad": "Avvecklad"}


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
      <p>En översikt över de API:er som Sundsvalls kommun delar som öppen källkod.</p>
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
          <p class="fact-box-link">
            <a href="{slug}-swagger.html">API-dokumentation (Swagger UI)</a>
          </p>
          <p class="fact-box-link">
            <a href="{repo_url}" rel="external">Källkod på GitHub</a>
          </p>
        </aside>
      </div>
    </div>
  </section>

  <section class="section section-slim" id="api-dokumentation">
    <div class="container">
      <h2>API-dokumentation</h2>
      <p class="section-intro">
        API:ets samtliga resurser, parametrar och datamodeller finns beskrivna i en
        OpenAPI-specifikation som är hämtad ur källkodsförrådet. Den kan utforskas
        interaktivt i Swagger UI eller laddas ner som YAML.
      </p>
      <div class="hero-actions">
        <a class="button button-primary" href="{slug}-swagger.html">Öppna Swagger UI</a>
        <a class="button button-outline" href="../assets/openapi/{slug}.yml" download>OpenAPI-specifikation (YAML)</a>
      </div>
    </div>
  </section>

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
    for api in apis:
        with open(os.path.join(OUT, f"{api['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(page(api))
        with open(os.path.join(OUT, f"{api['slug']}-swagger.html"), "w", encoding="utf-8") as f:
            f.write(swagger_page(api))
        spec = os.path.join(ROOT, "assets", "openapi", f"{api['slug']}.yml")
        if not os.path.exists(spec):
            raise SystemExit(f"missing OpenAPI spec: assets/openapi/{api['slug']}.yml")
    print(f"wrote {len(apis)} API pages (+ Swagger UI pages)")

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
