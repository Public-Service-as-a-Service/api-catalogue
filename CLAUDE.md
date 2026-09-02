# AI-instruktion: dokumentera ett API i API-katalogen

Den här filen beskriver hur en AI-assistent (eller människa) lägger till och
underhåller dokumentation av ett API i katalogen. Följ arbetssättet nedan –
det är så de befintliga sidorna är framtagna. Katalogen delar utseende och
struktur med systerkatalogen
[web-catalogue](https://github.com/Public-Service-as-a-Service/web-catalogue).

## Vad katalogen är

En statisk webbplats – en React-applikation som byggs med Vite – som är
Sundsvalls kommuns API-katalog: den beskriver de API:er som körs skarpt i produktion på kommunens
API-plattform. Många av API:erna utvecklas som öppen källkod på
[github.com/Sundsvallskommun](https://github.com/Sundsvallskommun) – repon som
börjar med `api-service` – men katalogen kan även omfatta API:er vars lösningar
inte publiceras som öppen källkod; att källkoden är öppen är sekundärt. Utöver
beskrivningssidorna exponeras varje API:s OpenAPI-specifikation interaktivt via
Swagger UI, och varje API:s programvaruförteckning (SBOM) i SPDX-format.
Publiceras till GitHub Pages via `.github/workflows/deploy-pages.yml` vid push
till `main` (arbetsflödet kör `npm ci && npm run build` och publicerar `dist/`).

## Designsystem – obligatoriskt

Webbplatsen följer [Sundsvalls kommuns designsystem](https://ui.sundsvall.dev/)
(dokumentation för AI-verktyg: <https://ui.sundsvall.dev/llms-full.txt>).

- **Importera komponenter från `@sk-web-gui/react`**: `Button`, `Card`, `Link`,
  `Label`, `Table`, `Breadcrumb`, `Header`, `Footer`, `Logo`, `GuiProvider`
  med flera. Bygg inte egna varianter av komponenter som designsystemet redan
  har.
- **Alla designtokens kommer från `@sk-web-gui/core`**, inkopplat som
  Tailwind-preset i `tailwind.config.js`. Använd tokenklasser som
  `bg-vattjom-background-200`, `text-dark-secondary`, `border-divider`,
  `font-header`, `text-lead`, `max-w-content`, `rounded-cards` samt
  avståndsskalan (`p-24`, `gap-16`, `py-40` …).
- **Hårdkoda aldrig hex-värden eller CSS-variabler.** Inga `#`-färger, inga
  `var(--…)` och ingen egen CSS utöver Tailwind-direktiven i `src/index.css` –
  allt utseende ska komma från paketen via komponenter och tokenklasser.
- `vattjom` (blå) är webbplatsens primärtema. Typsnitt: Raleway för rubriker
  via `font-header` (läses in från paketet `@fontsource/raleway`), Arial för
  brödtext (temats standard).
- **Knapptexter ska vara verb i imperativ** ("Öppna Swagger UI",
  "Ladda ner SPDX (JSON)") och **länktexter beskriva målet** ("Läs mer om
  Messaging" – aldrig bara "Läs mer").

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
`python3 scripts/generate-diagrams.py`. Generatorn skriver **sidskal** under
`api/` – head-metadata plus sidans data inbäddad som JSON i
`<script id="page-data">` – och innehållet renderas av React-komponenterna i
`src/pages/` (`ApiPage.tsx`, `SwaggerPage.tsx`, `SbomPage.tsx`) med
designsystemet. Startsidans kort behöver inte genereras:
`src/pages/IndexPage.tsx` importerar `apis-data.json` direkt. Fyll fälten
enligt tabellen ovan – uppgifterna ska vara härledda ur källkodsrepot. Ändras
sidornas struktur eller utseende görs det i React-komponenterna; ändras datat
körs generatorn om.

SBOM-sidan ingår inte i det här steget: den skapas först när
`refresh-sbom.yml` har lagt en `assets/sbom/<slug>.spdx.json` på plats. Ett nytt
API får alltså sin programvaruförteckning vid nästa schemalagda körning, eller
direkt om du kör workflowet manuellt.

## API-sidans struktur

Strukturen, som generatorn producerar:

Strukturen definieras av `src/pages/ApiPage.tsx`:

1. **Sidhuvud** – `SiteHeader` (designsystemets `Header` med kommunlogotypen).
2. **`PageHero`** – brödsmulor (Start / API:er / sidnamn, designsystemets
   `Breadcrumb`), `Label` med kategori och eventuell status, `h1` med API:ets
   namn och en menings sammanfattning.
3. **"Om API:et"** – 2–4 stycken verksamhetsnära text: vilket behov API:et
   löser, vilka som använder det, vilken nytta det ger. Därefter punktlistan
   "Det här gör API:et". I sidokolumnen en `FactBox` ("Snabbfakta") med
   version, kategori, status och målgrupp samt länkar till Swagger UI,
   programvaruförteckningen och källkoden.
4. **"API-dokumentation"** (id `api-dokumentation`) – knappar
   till Swagger UI-sidan, OpenAPI-specifikationen (YAML) och
   programvaruförteckningen. Knappraden visas så snart något av underlagen
   finns, så ett API utan incheckad spec får ändå sin SBOM-knapp.
5. **"Teknisk dokumentation"** (id `teknisk-dokumentation`) med
   underrubrikerna, i denna ordning: **Arkitektur** (diagram + prosa),
   **Teknikstack**, **Beroenden till andra mikrotjänster** (tabell: Tjänst,
   Version, Användning – versionerna ordagrant ur integrationsklienterna),
   **Programvaruförteckning** (antal komponenter och licenser, med länk vidare),
   **Konfiguration och driftsättning**, **Noterbart ur källkoden** (kodverifierade
   särdrag och README-avvikelser), **Källkod**.
6. **Sidfot** – `SiteFooter` (designsystemets `Footer`).

## Swagger UI-sidan

`api/<slug>-swagger.html` genereras av samma skript och renderas av
`src/pages/SwaggerPage.tsx`. Den använder samma sidhuvud/sidfot som övriga
sidor och renderar specifikationen från `assets/openapi/<slug>.yml` med
Swagger UI från npm-paketet `swagger-ui-dist` (`BaseLayout`, inga externa
CDN-beroenden). "Try it out" är avstängt, och serverlistan och
Authorize-knappen döljs via en Swagger UI-plugin, eftersom specens server-URL
är en genererad localhost-adress – riktiga anrop går via api.sundsvall.se.

## Programvaruförteckningen (SBOM)

`api/<slug>-sbom.html` genereras av samma skript ur
`assets/sbom/<slug>.spdx.json` – komponentlistan bäddas in i sidskalet som
JSON – och renderas av `src/pages/SbomPage.tsx`: tjänstens
tredjepartskomponenter med version och licens, en licenssammanfattning och ett
filterfält.

**Skriv aldrig SBOM-filerna för hand och regenerera dem inte som en del av det
vanliga arbetsflödet.** Till skillnad från sidorna och ritningarna, som är rena
funktioner av `apis-data.json`, är en SBOM en funktion av 75 externa repon som
Dependabot uppdaterar löpande. De underhålls därför av
`.github/workflows/refresh-sbom.yml`, som varje vecka checkar ut varje
källkodsrepo, kör Trivy och commitar det som ändrats. Workflowet publicerar
också till GitHub Pages i ett eget steg: en push som gjorts med `GITHUB_TOKEN`
startar inga nya workflows, så `deploy-pages.yml` plockar *inte* upp den
commiten.

Tre saker är avgörande om workflowet någon gång skrivs om:

- **Scanningen måste ske inifrån utcheckningen med `trivy fs … .`** Trivy
  härleder varje pakets `SPDXID` ur ett PkgID som innehåller scan-sökvägen, så
  `trivy fs src` i stället för `cd src && trivy fs .` byter identitet på samtliga
  paket och gör att hela filen skrivs om vid varje körning.
- **`--offline-scan` efter `mvn dependency:go-offline`.** En onlinescanning är
  dels ömtålig – Maven Central spärrar IP-adressen efter en handfull repon vid en
  svep över hela flottan – dels icke-deterministisk: en strypt körning
  rapporterar tyst licenser som `NOASSERTION` i stället för att fela, vilket
  hade gett en commit som inte motsvarar någon verklig beroendeändring. Offline
  ger identisk komponentlista till en kostnad av cirka 1 % av licensuppgifterna.
- **Trivy-versionen är pinnad** i workflowet, av samma skäl. En uppgradering ska
  vara en egen, granskad ändring.

`scripts/normalize-sbom.py` låser de fält som annars varierar mellan körningar
(dokumentets namnrymd och tidsstämpeln) till den scannade committen, tar bort
Trivys verktygsinterna annoteringar och skriver in härkomsten i dokumentet. Utan
det skulle varje veckokörning producera en commit även när inget beroende
ändrats.

Samma skript täpper också de licensluckor offlinescanningen lämnar
(`NOASSERTION`), i två steg som båda är rena funktioner av indata och därmed
inte bryter determinismen:

1. **Avstämning inom dokumentet** – i ett flermodulsrepo listas samma komponent
   dels ur modulens egen pom (med licens, ärvd ur föräldrakedjan), dels som
   beroende hos systermoduler (utan licens, eftersom reaktormoduler aldrig
   installeras i `~/.m2`). När alla licensierade poster för samma
   (namn, version) är överens fylls de tomma i från dem.
2. **`scripts/license-overrides.json`** – manuellt verifierade licenser för
   komponenter Trivy inte klarar (t.ex. `io.kubernetes:client-java`, vars
   föräldra-pom inte nås offline). Fyller **endast** i `licenseConcluded` när
   scanningen gav `NOASSERTION`/`NONE`; en licens Trivy själv hittat skrivs
   aldrig över, och `licenseDeclared` lämnas orörd. Varje post ska vara
   verifierad mot komponentens källrepo (länken i `källa`).

Komponenter som fortfarande saknar licens skrivs som `::warning::` och syns som
annoteringar på veckokörningen — dyker en ny upp (t.ex. efter en
Dependabot-bump): rätta i första hand vid källan (pom/metadata), i andra hand
med en ny post i override-filen. SBOM-sidorna visar `licenseConcluded` i första
hand och `licenseDeclared` som reserv.

Observera att SBOM-sidan visar varje komponent en gång, medan SPDX-dokumentet
behåller samtliga poster. Flermodulsrepon listar samma beroende per modul –
`api-service-operaton` har 12 `pom.xml` och 6 895 poster för 331 unika
komponenter.

**60-dagarsregeln.** GitHub stänger av schemalagda workflows i publika repon efter
60 dagar utan aktivitet i repot. Workflowet commitar bara när ett beroende faktiskt
ändrats, så ett par genuint tysta månader hade gett noll aktivitet och schemat hade
tystnat utan att någon märkte det. `keepalive`-jobbet återaktiverar därför workflowet
via API:et vid varje körning, oavsett om något ändrats.

GitHub dokumenterar varken vad som räknas som "repository activity" eller att
återaktivering nollställer räknaren — det är den bästa tillgängliga åtgärden, inte en
garanti. Jobbet loggar därför workflowets `state` före och efter, så att utfallet går
att se. Att commita sig levande vore alternativet, men keepalive-verktygen har gått
ifrån dummy-commits till just API-anropet.

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

All text mäts innan den ritas (`text_width` i generatorn, med teckenbredder för
Helvetica/Arial). Text som är bredare än sin låda kortas av med ellips, precis
som i systerkatalogen web-catalogue, så att etiketter aldrig hamnar utanför
lådan eller krockar med grannlådans text; hela texten behålls som `<title>` och
visas när muspekaren vilar över etiketten. Noteringarna under diagrammet
radbryts i stället på ordgränser. Korta därför inte av fälten i
`scripts/apis-data.json` för hand för att de ska "få plats" – skriv dem
fullständiga och låt generatorn sköta avkortningen. Fulltexten finns alltid på
API-sidan (beroendetabellen och "Noterbart ur källkoden").

## Övrigt att uppdatera

- **`README.md`** – uppdatera vid behov beskrivningen av innehållet.
- **Verifiera lokalt** innan push: kör `npx tsc --noEmit` och `npm run build`,
  servera `dist/` (`npm run preview`, kom ihåg `cp -r assets dist/assets` om du
  byggt utan npm-skriptet) och rendera sidorna med headless Chromium –
  kontrollera layout, diagram och att Swagger UI laddar specifikationen utan
  fel i konsolen.

## Arbetsflöde

Utveckla på en arbetsgren, committa och pusha, skapa PR mot `main` och merga
efter godkännande. Merge till `main` publicerar automatiskt via GitHub Pages.
