import { Card, Label } from '@sk-web-gui/react';
import apisData from '../../scripts/apis-data.json';
import { ButtonLink, FactBox, Hero, NoteBox, PageSection, TwoColumns } from '../components/blocks';
import { SiteFooter } from '../components/SiteFooter';
import { SiteHeader } from '../components/SiteHeader';
import { type ApiData, STATUS_LABEL } from '../types';

const apis = apisData as ApiData[];

const CATEGORY_ORDER = [
  'Kommunikation',
  'Ärendehantering',
  'Ekonomi och fakturering',
  'Dokument och arkiv',
  'Parts- och kunddata',
  'AI-tjänster',
  'Integration',
  'Samhällsservice',
  'Utbildning',
  'Utvecklingsverktyg',
];

const menu = [
  { label: 'Om katalogen', href: '#om-katalogen' },
  { label: 'API:er', href: '#apier' },
  { label: 'GitHub', href: 'https://github.com/Sundsvallskommun', external: true },
];

const footerLinks = [
  {
    label: 'Sundsvalls kommun på GitHub',
    href: 'https://github.com/Sundsvallskommun',
    external: true,
  },
  { label: 'sundsvall.se', href: 'https://sundsvall.se', external: true },
];

function ApiCard({ api }: { api: ApiData }) {
  const status = api.status ? STATUS_LABEL[api.status] : undefined;
  return (
    <Card color="mono" useHoverEffect href={`api/${api.slug}.html`}>
      <Card.Body>
        <div className="flex flex-wrap gap-8 pt-8">
          <Label inverted color="vattjom">
            {api.kategori}
          </Label>
          {status && <Label inverted>{status}</Label>}
        </div>
        <h3 className="font-header text-h4-sm md:text-h4-md xl:text-h4-lg text-dark-primary mt-12 mb-0">
          {api.namn}
        </h3>
        <p className="mt-8 mb-0">{api.ingress}</p>
        <p className="mt-12 mb-0 font-bold text-vattjom-text-primary">Läs mer om {api.namn} →</p>
      </Card.Body>
    </Card>
  );
}

export function IndexPage() {
  const byCategory = new Map<string, ApiData[]>();
  for (const api of apis) {
    const list = byCategory.get(api.kategori) ?? [];
    list.push(api);
    byCategory.set(api.kategori, list);
  }

  return (
    <>
      <SiteHeader menu={menu} homeHref="index.html" />
      <main>
        <Hero
          kicker="Sundsvalls kommun"
          title="En katalog över kommunens API:er"
          lead="Sundsvalls kommun bygger sina digitala tjänster på en gemensam plattform av mikrotjänster. Här hittar du en samlad översikt över de API:er som körs i produktion på kommunens API-plattform, med interaktiv API-dokumentation via Swagger UI."
          actions={
            <>
              <ButtonLink as="a" href="#apier" variant="primary" color="vattjom">
                Utforska API:erna
              </ButtonLink>
              <ButtonLink
                as="a"
                href="https://github.com/Sundsvallskommun"
                variant="secondary"
                color="vattjom"
              >
                Besök Sundsvalls kommun på GitHub
              </ButtonLink>
            </>
          }
        />

        <PageSection id="om-katalogen">
          <h2 className="font-header">Vad innehåller katalogen?</h2>
          <TwoColumns
            aside={
              <FactBox
                title="Snabbfakta"
                items={[
                  <>
                    <strong>Ett 70-tal</strong> API:er i skarp produktion
                  </>,
                  <>
                    Mikrotjänster bakom kommunens <strong>digitala tjänster</strong>
                  </>,
                  <>
                    Interaktiv dokumentation via <strong>Swagger UI</strong>
                  </>,
                  <>
                    Nås via kommunens <strong>API-plattform</strong>
                  </>,
                  <>
                    Många delas som <strong>öppen källkod</strong> på GitHub
                  </>,
                ]}
              />
            }
          >
            <p>
              Det här är Sundsvalls kommuns API-katalog: en samlad förteckning över de API:er som
              just nu körs skarpt i produktion på kommunens gemensamma API-plattform. Varje API
              listas under det namn och med den version som det exponeras med på plattformen.
            </p>
            <p>
              Varje API presenteras på en egen sida med två delar: en verksamhetsnära beskrivning
              av vad API:et gör och vilken nytta det skapar, samt en teknisk dokumentation för dig
              som vill förstå hur tjänsten är byggd eller vill återanvända den i din egen
              organisation. Dessutom kan varje API:s samtliga resurser och datamodeller utforskas
              interaktivt i Swagger UI, direkt ur tjänstens OpenAPI-specifikation.
            </p>
            <p>
              Kommunen arbetar enligt principen <em>öppen källkod först</em>, och många av
              API:erna delas därför på GitHub där de kan användas, granskas och vidareutvecklas av
              andra kommuner och organisationer. Katalogen omfattar dock även API:er vars
              lösningar inte publiceras som öppen källkod.
            </p>
          </TwoColumns>
        </PageSection>

        <PageSection id="apier" alt>
          <h2 className="font-header">API:er i katalogen</h2>
          <p className="text-lead">
            Katalogen omfattar de API:er som körs i produktion på kommunens gemensamma
            API-plattform, grupperade per område. Välj ett API för att läsa mer och utforska dess
            dokumentation.
          </p>
          {CATEGORY_ORDER.filter((cat) => byCategory.has(cat)).map((cat) => (
            <section key={cat} aria-label={cat}>
              <h3 className="font-header mt-40">{cat}</h3>
              <div className="mt-16 grid gap-24 md:grid-cols-2 xl:grid-cols-3">
                {(byCategory.get(cat) ?? [])
                  .slice()
                  .sort((a, b) => a.namn.toLowerCase().localeCompare(b.namn.toLowerCase(), 'sv'))
                  .map((api) => (
                    <ApiCard key={api.slug} api={api} />
                  ))}
              </div>
            </section>
          ))}
          <NoteBox>
            Katalogen visar de API:er, och de versioner, som körs skarpt i produktion vid
            ögonblicket. Avvecklade API:er och prototyper ingår inte. Nya API:er läggs till efter
            hand som de driftsätts.
          </NoteBox>
        </PageSection>
      </main>
      <SiteFooter
        title="API-katalogen"
        description="En översikt över de API:er som körs i produktion på Sundsvalls kommuns API-plattform."
        links={footerLinks}
      />
    </>
  );
}
