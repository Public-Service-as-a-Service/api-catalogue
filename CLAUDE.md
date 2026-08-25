# AI-instruktion: dokumentera ett API i API-katalogen

Den här filen beskriver hur en AI-assistent (eller människa) lägger till och
underhåller dokumentation av ett API i katalogen. Följ arbetssättet nedan –
det är så de befintliga sidorna är framtagna. Katalogen delar utseende och
struktur med systerkatalogen
[web-catalogue](https://github.com/Public-Service-as-a-Service/web-catalogue).

## Vad katalogen är

En statisk webbplats (ren HTML/CSS, inget byggsteg) som är Sundsvalls kommuns
API-katalog: den beskriver de API:er som körs skarpt i produktion på kommunens
API-plattform. Många av API:erna utvecklas som öppen källkod på
[github.com/Sundsvallskommun](https://github.com/Sundsvallskommun) – repon som
börjar med `api-service` – men katalogen kan även omfatta API:er vars lösningar
inte publiceras som öppen källkod; att källkoden är öppen är sekundärt. Utöver
beskrivningssidorna exponeras varje API:s OpenAPI-specifikation interaktivt via
Swagger UI. Publiceras till GitHub Pages via
`.github/workflows/deploy-pages.yml` vid push till `main`.

## Grundprinciper

1. **Endast API:er i skarp produktion.** Katalogen listar de API:er, och de
   versioner, som körs i produktion vid ögonblicket. Avvecklade API:er och
   prototyper ska inte finnas i katalogen – när ett API tas ur drift tas dess
   post bort ur `scripts/apis-data.json` tillsammans med de genererade filerna
   (API-sidan, Swagger UI-sidan, OpenAPI-specifikationen och diagrammet),
   varefter generatorskripten körs om.
2. **API-plattformens namn, inte reponamn.** API:er presenteras under det namn
   de exponeras med på kommunens API-plattform (`info.title` i
   OpenAPI-specifikationen), t.ex. "Messaging" – inte `api-service-messaging`.
3. **En sida per API** plus en Swagger UI-sida. Sidan heter `api/<slug>.html`
   och Swagger UI-sidan `api/<slug>-swagger.html` (slug utan å/ä/ö, med
   bindestreck, härledd ur API-namnet).
4. **Koden är sanningskällan, inte README.** README-filer kan vara inaktuella.
   Härled alltid teknisk fakta (beroenden, versioner, beteenden) ur
   källkodsrepots konfiguration och kod. Verifierade avvikelser från README har
   företräde och noteras under "Noterbart ur källkoden".
5. **Två delar på samma sida.** Varje API-sida har först en verksamhetsnära
   beskrivning (utan tekniska utvecklingsdetaljer), därefter en sektion
   "Teknisk dokumentation" – på samma sida, inte en undersida. Däremellan en
   sektion "API-dokumentation" med länkar till Swagger UI och specifikationen.
6. **Allt innehåll på svenska.**

## Så härleder du teknisk fakta ur ett `api-service`-repo

Klona repot (grunt räcker: `git clone --depth 1 …`) och undersök:

| Fakta | Källa i repot |
| --- | --- |
| API-namn och version | `info.title` och `info.version` i OpenAPI-specifikationen samt `<version>` i `pom.xml`. |
| OpenAPI-specifikation | `src/integration-test/resources/openapi.yml` (dept44-standard: specen checkas in och verifieras mot den genererade i integrationstesterna). Kopieras till `assets/openapi/<slug>.yml`. |
| Beroende mikrotjänster och versioner | `src/main/resources/integrations/*.yml` – en klientspecifikation per beroende tjänst, med version i filnamn/innehåll. Paketen under `src/main/java/**/integration/` bekräftar vilka som faktiskt används i koden. |
| Externa integrationer | Integrationspaket som inte är kommun-API:er (t.ex. `slack`) samt beroenden i `pom.xml` (t.ex. `slack-api-client`). |
| Teknikstack | `pom.xml`: förälder `dept44-service-parent` ⇒ Spring Boot via kommunens tjänsteplattform dept44 (ange versionen); Java-version ur pom/README. |
| Databas | `spring.flyway`/`spring.jpa` i `src/main/resources/application.yml` och migrationsfiler under `src/main/resources/db/migration` (MariaDB är standard). |
| Beteenden och särdrag | Tjänstelagret under `src/main/java/**/service/` – verifiera påståenden i koden (t.ex. Messagings letter-routning: digital brevlåda först, därefter fysisk post). |
| Konfiguration | `application.yml`: integrations-URL:er, OAuth2-klientuppgifter, databasanslutning, funktionsinställningar. |

Alla API:er exponeras via kommunens API-plattform (WSO2) på api.sundsvall.se
och anropas med OAuth2-klientuppgifter; `municipalityId` ingår normalt i
API-vägarna.

## Så skapas API-sidor

**Datadrivet (enda sättet).** Lägg till ett objekt i `scripts/apis-data.json`
med de fält som redan finns där (repo, namn, slug, kategori, status,
apiVersion, ingress, beskrivning, malgrupp, funktioner, beroenden,
integrationer, databas, teknik, konfiguration, anteckningar), kopiera
OpenAPI-specifikationen till `assets/openapi/<slug>.yml` och kör
`python3 scripts/generate-pages.py` följt av
`python3 scripts/generate-diagrams.py`. API-sidan, Swagger UI-sidan,
arkitekturritningen och startsidans kort (mellan `API-CARDS`-markörerna i
`index.html`) genereras då automatiskt med rätt struktur. Fyll fälten enligt
tabellen ovan – uppgifterna ska vara härledda ur källkodsrepot.

## API-sidans struktur

Strukturen, som generatorn producerar:

1. **Sidhuvud** – samma `site-header` som övriga sidor (länkar med `../`).
2. **`page-hero`** – brödsmulor (Start / API:er / sidnamn), `app-tag
   app-tag-light` med kategori, `h1` med API:ets namn, `hero-lead` med en
   menings sammanfattning.
3. **"Om API:et"** – 2–4 stycken verksamhetsnära text: vilket behov API:et
   löser, vilka som använder det, vilken nytta det ger. Därefter punktlistan
   "Det här gör API:et". I sidokolumnen en `fact-box` ("Snabbfakta") med
   version, kategori, status och målgrupp samt länkar till Swagger UI och
   källkoden.
4. **"API-dokumentation"** (`section-slim`, id `api-dokumentation`) – knappar
   till Swagger UI-sidan och OpenAPI-specifikationen (YAML).
5. **"Teknisk dokumentation"** (`section-alt`, id `teknisk-dokumentation`) med
   underrubrikerna, i denna ordning: **Arkitektur** (diagram + prosa),
   **Teknikstack**, **Beroenden till andra mikrotjänster** (tabell: Tjänst,
   Version, Användning – versionerna ordagrant ur integrationsklienterna),
   **Konfiguration och driftsättning**, **Noterbart ur källkoden** (kodverifierade
   särdrag och README-avvikelser), **Källkod**.
6. **Sidfot** – samma `site-footer` som övriga sidor.

## Swagger UI-sidan

`api/<slug>-swagger.html` genereras av samma skript. Den använder samma
sidhuvud/sidfot som övriga sidor, en kompakt `page-hero` och renderar
specifikationen från `assets/openapi/<slug>.yml` med Swagger UI
(versionen ligger incheckad i `assets/vendor/swagger-ui/`, `BaseLayout`,
inga externa CDN-beroenden). "Try it out" är avstängt och
serverlistan dold, eftersom specens server-URL är en genererad
localhost-adress – riktiga anrop går via api.sundsvall.se.

## Arkitekturritningen

En SVG per API i `assets/diagrams/<samma slug>.svg`, genererad ur
`scripts/apis-data.json` med `scripts/generate-diagrams.py`. Rita aldrig för
hand – generatorn håller stil och layout konsekvent.

Ritningens lager, uppifrån och ned:

1. **Konsumerande applikationer** (grå, streckad) – webbappar och
   verksamhetssystem.
2. **API-plattform (WSO2)** (grå med mörk ram) – all trafik går genom den;
   pilen märks med OAuth2/klientuppgifter.
3. **Detta API** (blå) – med teknikstack och reponamn som undertext, samt
   eventuell databas (gul) till höger.
4. **Beroende mikrotjänster** (grön grupp) – tjänster som API:et anropar, med
   version och kort användningstext.
5. **Externa system och integrationer** (grå grupp, streckade) – t.ex. Slack.
6. **Noteringar och teckenförklaring** nederst – kodverifierade särdrag.

Innehållet i diagrammet (beroenden, versioner, noteringar) ska stämma exakt
med sidans beroendetabell – båda kommer från samma fält i datafilen.

## Övrigt att uppdatera

- **`index.html`** – korten mellan `<!-- BEGIN:API-CARDS -->` och
  `<!-- END:API-CARDS -->` genereras av `scripts/generate-pages.py`
  (grupperade per kategori, sorterade på namn); redigera aldrig det blocket
  för hand.
- **`README.md`** – uppdatera vid behov beskrivningen av innehållet.
- **Verifiera lokalt** innan push: rendera sidorna med headless Chromium och
  kontrollera layout, diagram och att Swagger UI laddar specifikationen utan
  fel i konsolen.

## Arbetsflöde

Utveckla på en arbetsgren, committa och pusha, skapa PR mot `main` och merga
efter godkännande. Merge till `main` publicerar automatiskt via GitHub Pages.
