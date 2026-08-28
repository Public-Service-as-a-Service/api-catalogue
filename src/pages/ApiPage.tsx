import { Label, Link, Table } from '@sk-web-gui/react';
import {
  ButtonLink,
  DiagramFigure,
  FactBox,
  PageHero,
  PageSection,
  TwoColumns,
} from '../components/blocks';
import { SubpageChrome } from '../components/SubpageChrome';
import { type ApiData, STATUS_LABEL } from '../types';

export interface ApiPageData {
  api: ApiData;
  hasSpec: boolean;
  hasSbom: boolean;
  sbom: { komponenter: number; licenser: number } | null;
}

function archProse(api: ApiData): string {
  const t = api.teknik ?? {};
  const bits: string[] = [];
  const stack = [t.sprak, t.ramverk].filter(Boolean).join(', ');
  if (stack) {
    bits.push(`API:et är en mikrotjänst (${stack}).`);
  } else {
    bits.push('API:et är en mikrotjänst; se källkoden för detaljer om uppbyggnaden.');
  }
  bits.push(
    'Konsumenter når tjänsten via kommunens gemensamma API-plattform (WSO2) på api.sundsvall.se – tjänsten anropas aldrig direkt.',
  );
  if (api.beroenden?.length) {
    bits.push('Tjänsten anropar i sin tur andra mikrotjänster i kommunens tjänstelandskap.');
  }
  if (api.databas) {
    bits.push(`Lagring: ${api.databas}.`);
  }
  if (api.integrationer?.length) {
    bits.push(`Övriga integrationer som förekommer i koden: ${api.integrationer.join(', ')}.`);
  }
  return bits.join(' ');
}

export function ApiPage({ data }: { data: ApiPageData }) {
  const { api, hasSpec, hasSbom, sbom } = data;
  const repoUrl = `https://github.com/Sundsvallskommun/${api.repo}`;
  const status = api.status ? STATUS_LABEL[api.status] : undefined;
  const teknik = api.teknik ?? {};
  const beroenden = api.beroenden ?? [];
  const konfiguration = api.konfiguration ?? [];
  const anteckningar = api.anteckningar ?? [];

  return (
    <SubpageChrome>
      <PageHero
        crumbs={[
          { label: 'Start', href: '../index.html' },
          { label: 'API:er', href: '../index.html#apier' },
          { label: api.namn },
        ]}
        tags={
          <>
            <Label inverted color="vattjom">
              {api.kategori}
            </Label>
            {status && <Label inverted>{status}</Label>}
          </>
        }
        title={api.namn}
        lead={api.ingress}
      />

      <PageSection>
        <h2 className="font-header">Om API:et</h2>
        <TwoColumns
          aside={
            <FactBox
              title="Snabbfakta"
              items={[
                <>
                  Version: <strong>{api.apiVersion ?? '–'}</strong>
                </>,
                <>
                  Kategori: <strong>{api.kategori}</strong>
                </>,
                <>
                  Status: <strong>{status ?? 'Aktiv'}</strong>
                </>,
                <>
                  Målgrupp: <strong>{api.malgrupp ?? '–'}</strong>
                </>,
              ]}
              links={[
                ...(hasSpec
                  ? [{ label: 'API-dokumentation (Swagger UI)', href: `${api.slug}-swagger.html` }]
                  : []),
                ...(hasSbom
                  ? [{ label: 'Programvaruförteckning (SBOM)', href: `${api.slug}-sbom.html` }]
                  : []),
                { label: 'Källkod på GitHub', href: repoUrl },
              ]}
            />
          }
        >
          {(api.beskrivning ?? []).map((stycke, i) => (
            <p key={i}>{stycke}</p>
          ))}
          <h3 className="font-header">Det här gör API:et</h3>
          <ul className="flex flex-col gap-8 pl-20 list-disc">
            {(api.funktioner ?? []).map((f) => (
              <li key={f.titel}>
                <strong>{f.titel}</strong> – {f.text}
              </li>
            ))}
          </ul>
        </TwoColumns>
      </PageSection>

      <PageSection id="api-dokumentation" alt>
        <h2 className="font-header">API-dokumentation</h2>
        <p className="text-lead">
          {hasSpec
            ? 'API:ets samtliga resurser, parametrar och datamodeller finns beskrivna i en OpenAPI-specifikation som är hämtad ur källkodsförrådet. Den kan utforskas interaktivt i Swagger UI eller laddas ner som YAML.'
            : 'Ingen incheckad OpenAPI-specifikation hittades i källkodsförrådet; se källkoden för aktuell API-dokumentation.'}
          {hasSbom &&
            ' Programvaruförteckningen (SBOM) listar tjänstens samtliga tredjepartskomponenter med version och licens.'}
        </p>
        {(hasSpec || hasSbom) && (
          <div className="mt-24 flex flex-wrap gap-16">
            {hasSpec && (
              <>
                <ButtonLink
                  as="a"
                  href={`${api.slug}-swagger.html`}
                  variant="primary"
                  color="vattjom"
                >
                  Öppna Swagger UI
                </ButtonLink>
                <ButtonLink
                  as="a"
                  href={`../assets/openapi/${api.slug}.yml`}
                  download
                  variant="secondary"
                  color="vattjom"
                >
                  Ladda ner OpenAPI-specifikationen (YAML)
                </ButtonLink>
              </>
            )}
            {hasSbom && (
              <ButtonLink
                as="a"
                href={`${api.slug}-sbom.html`}
                variant="secondary"
                color="vattjom"
              >
                Visa programvaruförteckningen (SBOM)
              </ButtonLink>
            )}
          </div>
        )}
      </PageSection>

      <PageSection id="teknisk-dokumentation">
        <h2 className="font-header">Teknisk dokumentation</h2>
        <p className="text-lead">
          Nedan beskrivs hur tjänsten är uppbyggd, vilka andra tjänster den anropar och vad som
          krävs för att driftsätta den. Informationen är härledd ur källkoden och dess
          konfiguration på GitHub.
        </p>

        <h3 className="font-header">Arkitektur</h3>
        <DiagramFigure
          src={`../assets/diagrams/${api.slug}.svg`}
          alt={`Arkitekturskiss för ${api.namn}: tjänstens delar och dess integrationer.`}
        >
          Lösningsarkitektur, härledd ur källkodens konfiguration.
        </DiagramFigure>
        <p>{archProse(api)}</p>

        <h3 className="font-header">Teknikstack</h3>
        <ul className="flex flex-col gap-8 pl-20 list-disc">
          {teknik.sprak && (
            <li>
              <strong>Språk:</strong> {teknik.sprak}
            </li>
          )}
          {teknik.ramverk && (
            <li>
              <strong>Ramverk:</strong> {teknik.ramverk}
            </li>
          )}
          {api.databas && (
            <li>
              <strong>Databas:</strong> {api.databas}
            </li>
          )}
          {teknik.ovrigt && (
            <li>
              <strong>Övrigt:</strong> {teknik.ovrigt}
            </li>
          )}
          {!teknik.sprak && !teknik.ramverk && !api.databas && !teknik.ovrigt && (
            <li>Se källkodens byggfiler för detaljer.</li>
          )}
        </ul>

        <h3 className="font-header">Beroenden till andra mikrotjänster</h3>
        {beroenden.length > 0 ? (
          <>
            <p>
              Tjänsten anropar följande mikrotjänster. Versionerna är hämtade ur källkodens
              integrationsklienter.
            </p>
            <div className="overflow-x-auto">
              <Table background aria-label={`Mikrotjänster som ${api.namn} anropar`}>
                <Table.Header>
                  <Table.HeaderColumn>Tjänst</Table.HeaderColumn>
                  <Table.HeaderColumn>Version</Table.HeaderColumn>
                  <Table.HeaderColumn>Användning</Table.HeaderColumn>
                </Table.Header>
                <Table.Body>
                  {beroenden.map((d) => (
                    <Table.Row key={d.name}>
                      <Table.Column>{d.name}</Table.Column>
                      <Table.Column>{d.version ?? '–'}</Table.Column>
                      <Table.Column>{d.usage ?? ''}</Table.Column>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </div>
          </>
        ) : (
          <p>Inga anrop till andra mikrotjänster hittades i källkodens konfiguration.</p>
        )}

        {hasSbom && sbom && (
          <>
            <h3 className="font-header">Programvaruförteckning</h3>
            <p>
              Tjänsten bygger på {sbom.komponenter} tredjepartskomponenter fördelade på{' '}
              {sbom.licenser} olika licenser. Till skillnad från tabellen ovan, som listar andra
              mikrotjänster, avses här de programbibliotek som ingår i bygget. Se{' '}
              <Link href={`${api.slug}-sbom.html`}>programvaruförteckningen</Link> för hela
              listan.
            </p>
          </>
        )}

        <h3 className="font-header">Konfiguration och driftsättning</h3>
        <ul className="flex flex-col gap-8 pl-20 list-disc">
          {konfiguration.length > 0 ? (
            konfiguration.map((k, i) => <li key={i}>{k}</li>)
          ) : (
            <li>Se källkodens miljöfilsexempel.</li>
          )}
        </ul>

        {anteckningar.length > 0 && (
          <>
            <h3 className="font-header">Noterbart ur källkoden</h3>
            <ul className="flex flex-col gap-8 pl-20 list-disc">
              {anteckningar.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          </>
        )}

        <h3 className="font-header">Källkod</h3>
        <p>
          Källkoden är öppen och finns hos{' '}
          <Link href={repoUrl} external>
            Sundsvalls kommun på GitHub
          </Link>
          . I källkodsförrådet finns även instruktioner för att klona, konfigurera och starta
          tjänsten i egen miljö.
        </p>
      </PageSection>
    </SubpageChrome>
  );
}
