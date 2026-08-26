# API-katalogen

Sundsvalls kommuns API-katalog: en förteckning över de API:er som körs i
produktion på kommunens API-plattform, med de versioner som är driftsatta.
Avvecklade API:er och prototyper ingår inte. Många av API:erna utvecklas som
öppen källkod på GitHub
([github.com/Sundsvallskommun](https://github.com/Sundsvallskommun)
– repon som börjar med `api-service`), men katalogen omfattar även API:er vars
lösningar inte publiceras som öppen källkod.

Katalogen beskriver API:erna på ett lättillgängligt sätt: vad varje API gör,
vem det är till för och vilken nytta det skapar – och exponerar dessutom varje
API:s fullständiga dokumentation interaktivt via Swagger UI, direkt ur
tjänstens OpenAPI-specifikation.

Varje API presenteras på en egen sida med en verksamhetsnära beskrivning följt
av teknisk dokumentation (härledd från GitHub) på samma sida, samt en
Swagger UI-sida för den interaktiva API-dokumentationen.

## Innehåll

- `index.html` – förstasidan med information om katalogen och en översikt över
  API:erna, grupperad per kategori.
- `api/<slug>.html` – en sida per API (ett 70-tal), med beskrivning och
  teknisk dokumentation. Genereras från `scripts/apis-data.json` med
  `scripts/generate-pages.py`.
- `api/<slug>-swagger.html` – Swagger UI-sida per API som renderar
  OpenAPI-specifikationen interaktivt.
- `assets/openapi/<slug>.yml` – API:ets OpenAPI-specifikation, hämtad ur
  källkodsrepots incheckade spec.
- `api/<slug>-sbom.html` – programvaruförteckning per API: tredjepartskomponenter
  med version och licens, plus en licenssammanfattning.
- `assets/sbom/<slug>.spdx.json` – förteckningen i SPDX-format, maskinellt
  härledd ur källkodsrepots beroendeträd.
- `scripts/apis-data.json` – fakta om varje API, härledd ur respektive
  källkodsrepo.
- `assets/styles.css` – webbplatsens utseende.
- `assets/diagrams/*.svg` – arkitekturritningar, genererade med
  `scripts/generate-diagrams.py`.
- `CLAUDE.md` – AI-instruktion som i detalj beskriver hur ett API
  dokumenteras i katalogen.
- `scripts/normalize-sbom.py` – gör Trivys SPDX-utdata reproducerbar så att en
  oförändrad beroendelista inte ger någon diff.
- `.github/workflows/deploy-pages.yml` – arbetsflöde som publicerar webbplatsen
  till GitHub Pages.
- `.github/workflows/refresh-sbom.yml` – arbetsflöde som varje vecka uppdaterar
  programvaruförteckningarna från källkodsrepona.

## Publicering

Webbplatsen är statisk och kräver inget byggsteg. Den publiceras automatiskt via
GitHub Pages när ändringar pushas till `main`-grenen.

Engångsinställning: under **Settings → Pages** i repot, välj **GitHub Actions**
som källa ("Source"). Därefter publiceras sidan på
`https://<organisation>.github.io/api-catalogue/` vid varje push till `main`
(eller manuellt via *Run workflow*).

Webbplatsen kan även driftsättas som container: `Dockerfile` bygger en
nginx-avbildning som serverar sidan på port 80 (används för deploy via
Dokploy – byggtyp Dockerfile, containerport 80, med webhook som triggar
deploy vid push till `main`).

## Lägga till fler API:er

Följ instruktionen i [`CLAUDE.md`](CLAUDE.md) – den beskriver i detalj hur
teknisk fakta härleds ur källkodsrepot (API-version och OpenAPI-spec ur repots
incheckade specifikation, beroende tjänster ur integrationsklienterna), hur
API-sidan struktureras och hur arkitekturritningen genereras.

Kort version: kopiera API:ets OpenAPI-specifikation till
`assets/openapi/<slug>.yml`, lägg till ett objekt i `scripts/apis-data.json`
och kör `python3 scripts/generate-pages.py` följt av
`python3 scripts/generate-diagrams.py`. Sidorna, Swagger UI-sidan,
arkitekturritningen och startsidans kort genereras då automatiskt.
