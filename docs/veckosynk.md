# Schemalagd veckosynk av API-katalogen

Katalogen hålls i synk med produktionen av ett schemalagt Claude-jobb – en
*Routine* i Claude Code på webben – som varje **måndag 06:00 UTC** (08:00
svensk sommartid, 07:00 vintertid) startar en färsk session i katalogens
utvecklingsmiljö. Tidpunkten är vald med flit: den ligger *efter* den
ordinarie SBOM-körningen (`.github/workflows/refresh-sbom.yml`, måndagar
05:00 UTC), så att veckans SBOM:er redan är färska när katalogsynken börjar.

Routinen är knuten till ett konto på claude.ai och syns/pausas/ändras under
**Routines** i Claude Code på webben (eller genom att be Claude lista och
uppdatera den med trigger-verktygen). Den här filen är den granskningsbara
beskrivningen av vad jobbet gör; sessionen som routinen startar instrueras
att läsa och följa den, och vid konflikt har den här filen företräde framför
routinens inbäddade prompt. Ändringar i arbetssättet görs alltså via PR mot
den här filen.

## Steg 1 – synka katalogen mot källkodsrepona

1. Läs `CLAUDE.md` i repots rot – den styr hur katalogen underhålls och hur
   teknisk fakta härleds ur ett `api-service`-repo.
2. Utgå från `scripts/apis-data.json`; fältet `repo` pekar på källkodsrepot
   under `github.com/Sundsvallskommun`.
3. **Nya API:er.** Lista organisationens repon som börjar med `api-service-`
   och som saknas i datafilen. Klona kandidaterna grunt och bedöm om de är i
   skarp produktion (incheckad OpenAPI-specifikation, releaser/taggar,
   version ≥ 1.0, aktiv historik). Lägg bara till API:er där bedömningen är
   säker; lista osäkra kandidater i PR-beskrivningen i stället för att gissa
   – granskaren avgör.
4. **Avvecklade API:er.** Poster vars källkodsrepo är arkiverat eller
   borttaget behandlas som avvecklade: ta bort posten ur `apis-data.json`
   tillsammans med de genererade filerna (`api/<slug>.html`,
   `api/<slug>-swagger.html`, `api/<slug>-sbom.html`,
   `assets/openapi/<slug>.yml`, `assets/diagrams/<slug>.svg`,
   `assets/sbom/<slug>.spdx.json`). Är repot kvar men API:et misstänks vara
   ur drift av andra skäl: flagga i PR-beskrivningen i stället för att ta
   bort.
5. **Ändrade API:er.** Klona varje kvarvarande repo grunt och jämför med
   posten: `info.version` i OpenAPI-specifikationen mot `apiVersion`,
   integrationsklienterna under `src/main/resources/integrations/` mot
   beroendetabellen, databas, teknikstack och särdrag enligt tabellen i
   `CLAUDE.md`. Uppdatera posten och kopiera in den nya specifikationen till
   `assets/openapi/<slug>.yml` när den ändrats.
   **Även verksamhetsbeskrivningen ingår i jämförelsen.** Har källrepots
   README eller specens `info.description` ändrats sedan posten skrevs,
   eller stämmer postens bild av API:et inte längre, omprövas ingress,
   beskrivning och målgrupp. README är aldrig ensam sanningskälla:
   verifiera varje ändrad uppgift i koden (tjänstelagret, resurserna i
   specen) innan posten ändras – i webbkatalogen missades i augusti 2026
   på det här sättet att två tjänster sedan länge betjänade även
   privatpersoner. En README-uppgift utan kodtäckning flaggas i
   PR-beskrivningen i stället för att skrivas in.
6. Kör `python3 scripts/generate-pages.py` följt av
   `python3 scripts/generate-diagrams.py` och verifiera sidorna lokalt med
   headless Chromium enligt `CLAUDE.md`.
7. **Inget skiljer?** Avsluta utan PR och utan brus.
8. Annars: committa på en arbetsgren (`claude/veckosynk-<datum>`), pusha och
   skapa PR mot `main` med en sammanfattning uppdelad i *nya*, *borttagna*
   och *ändrade* API:er samt eventuella osäkra kandidater. Prenumerera på
   PR:en och driv den till grönt. Merga aldrig själv – en människa godkänner.

## Steg 2 – SBOM för nya och ändrade API:er

Programvaruförteckningarna underhålls uteslutande av
`.github/workflows/refresh-sbom.yml`; de skrivs aldrig för hand (se
`CLAUDE.md`). Steg 2 börjar först när PR:en från steg 1 är mergad till
`main`, eftersom workflowets matris läser `apis-data.json` från `main`:

- **Nya API:er:** starta `refresh-sbom.yml` manuellt (workflow_dispatch) med
  input `only=<slug>`, en körning per nytt API, så att förteckningen kommer
  på plats direkt i stället för vid nästa veckokörning.
- **Ändrade API:er:** täcks normalt redan av samma morgons ordinarie körning
  (05:00 UTC). Starta workflowet för en slug bara om källrepots beroenden
  ändrats efter den körningen.
- **Borttagna API:er:** deras SBOM-filer togs redan bort i steg 1; workflowet
  rör dem inte.

Bevaka att de startade körningarna går igenom; en röd körning felsöks enligt
kommentarerna i workflowfilen.

## Avslut

Sessionen bokar egna avstämningar (ca en timme) tills PR:en är mergad eller
stängd och eventuella SBOM-körningar är klara, och avslutar därefter. Merge
till `main` publicerar katalogen via GitHub Pages som vanligt.
