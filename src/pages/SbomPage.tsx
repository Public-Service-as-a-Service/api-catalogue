import { FormControl, FormLabel, Input, Label, Link, Table } from '@sk-web-gui/react';
import { useMemo, useState } from 'react';
import { ButtonLink, PageHero, PageSection } from '../components/blocks';
import { SubpageChrome } from '../components/SubpageChrome';
import type { SbomKomponent, SbomProvenans } from '../types';

export interface SbomPageData {
  api: { slug: string; namn: string; kategori: string; repo: string };
  komponenter: SbomKomponent[];
  licenser: [string, number][];
  provenans: SbomProvenans;
}

export function SbomPage({ data }: { data: SbomPageData }) {
  const { api, komponenter, licenser, provenans } = data;
  const repoUrl = `https://github.com/Sundsvallskommun/${api.repo}`;
  const datum = provenans.created.slice(0, 10);
  const [filter, setFilter] = useState('');

  const visade = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return komponenter;
    return komponenter.filter((k) =>
      `${k.namn} ${k.version} ${k.licens}`.toLowerCase().includes(q),
    );
  }, [filter, komponenter]);

  return (
    <SubpageChrome>
      <PageHero
        crumbs={[
          { label: 'Start', href: '../index.html' },
          { label: 'API:er', href: '../index.html#apier' },
          { label: api.namn, href: `${api.slug}.html` },
          { label: 'SBOM' },
        ]}
        tags={
          <Label inverted color="vattjom">
            {api.kategori}
          </Label>
        }
        title={`${api.namn} – programvaruförteckning`}
        lead="Samtliga tredjepartskomponenter som ingår i tjänstens bygge, med version och licens. Förteckningen är maskinellt härledd ur källkodens beroendeträd och publiceras i SPDX-format."
        actions={
          <>
            <ButtonLink
              as="a"
              href={`../assets/sbom/${api.slug}.spdx.json`}
              download
              variant="primary"
              color="vattjom"
            >
              Ladda ner SPDX (JSON)
            </ButtonLink>
            <ButtonLink as="a" href={`${api.slug}.html`} variant="secondary" color="vattjom">
              Gå tillbaka till {api.namn}
            </ButtonLink>
          </>
        }
      />

      <PageSection id="om-forteckningen">
        <h2 className="font-header">Om förteckningen</h2>
        <ul className="flex flex-col gap-8 pl-20 list-disc">
          <li>
            Antal komponenter: <strong>{komponenter.length}</strong>
          </li>
          <li>
            Antal unika licenser: <strong>{licenser.length}</strong>
          </li>
          <li>
            Källa: <strong>{provenans.namn}</strong> (
            <Link href={repoUrl} external>
              källkod på GitHub
            </Link>
            )
          </li>
          <li>
            Avser källkod från: <strong>{datum}</strong>
          </li>
          <li>
            Format: <strong>{provenans.spdx}</strong>, genererad med{' '}
            <strong>{provenans.verktyg}</strong>
          </li>
        </ul>
        <p>
          Förteckningen uppdateras automatiskt och beskriver beroendena i tjänstens huvudgren vid
          angivet datum. Den avser programbibliotek – vilka andra mikrotjänster API:et anropar
          framgår av{' '}
          <Link href={`${api.slug}.html#teknisk-dokumentation`}>den tekniska dokumentationen</Link>
          .
        </p>
      </PageSection>

      <PageSection id="licenser" alt>
        <h2 className="font-header">Licenser</h2>
        <p className="text-lead">Fördelning av deklarerade licenser bland komponenterna.</p>
        <div className="mt-24 overflow-x-auto">
          <Table background aria-label={`Licensfördelning för ${api.namn}`}>
            <Table.Header>
              <Table.HeaderColumn>Licens</Table.HeaderColumn>
              <Table.HeaderColumn>Antal komponenter</Table.HeaderColumn>
            </Table.Header>
            <Table.Body>
              {licenser.map(([licens, antal]) => (
                <Table.Row key={licens}>
                  <Table.Column>{licens}</Table.Column>
                  <Table.Column>{antal}</Table.Column>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        </div>
      </PageSection>

      <PageSection id="komponenter">
        <h2 className="font-header">Komponenter</h2>
        <p className="text-lead">
          Samtliga {komponenter.length} komponenter, inklusive transitiva beroenden.
        </p>
        <FormControl className="mt-24 max-w-content">
          <FormLabel>Filtrera listan</FormLabel>
          <Input
            type="search"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Sök på komponent eller licens"
            autoComplete="off"
          />
        </FormControl>
        <p aria-live="polite" className="text-small text-dark-secondary">
          {filter.trim() ? `${visade.length} av ${komponenter.length}` : ' '}
        </p>
        <div className="overflow-x-auto">
          <Table background dense aria-label={`Tredjepartskomponenter i ${api.namn}`}>
            <Table.Header>
              <Table.HeaderColumn>Komponent</Table.HeaderColumn>
              <Table.HeaderColumn>Version</Table.HeaderColumn>
              <Table.HeaderColumn>Licens</Table.HeaderColumn>
            </Table.Header>
            <Table.Body>
              {visade.map((k) => (
                <Table.Row key={`${k.namn}@${k.version}@${k.licens}`}>
                  <Table.Column>{k.namn}</Table.Column>
                  <Table.Column>{k.version}</Table.Column>
                  <Table.Column>{k.licens}</Table.Column>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        </div>
      </PageSection>
    </SubpageChrome>
  );
}
