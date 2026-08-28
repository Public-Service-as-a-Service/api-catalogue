import { Label, Link } from '@sk-web-gui/react';
import { useEffect, useRef } from 'react';
import { SwaggerUIBundle } from 'swagger-ui-dist';
import 'swagger-ui-dist/swagger-ui.css';
import { PageHero, PageSection } from '../components/blocks';
import { SubpageChrome } from '../components/SubpageChrome';

export interface SwaggerPageData {
  api: { slug: string; namn: string; kategori: string; apiVersion?: string | null };
}

export function SwaggerPage({ data }: { data: SwaggerPageData }) {
  const { api } = data;
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    SwaggerUIBundle({
      url: `../assets/openapi/${api.slug}.yml`,
      domNode: container.current,
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis],
      // Serverlistan och Authorize-knappen döljs: specens server-URL är en
      // genererad localhost-adress – riktiga anrop går via api.sundsvall.se.
      plugins: [
        () => ({
          components: {
            ServersContainer: () => null,
            AuthorizeBtnContainer: () => null,
          },
        }),
      ],
      layout: 'BaseLayout',
      docExpansion: 'list',
      defaultModelsExpandDepth: 0,
      validatorUrl: null,
      tryItOutEnabled: false,
      supportedSubmitMethods: [],
    });
  }, [api.slug]);

  return (
    <SubpageChrome>
      <PageHero
        crumbs={[
          { label: 'Start', href: '../index.html' },
          { label: 'API:er', href: '../index.html#apier' },
          { label: api.namn, href: `${api.slug}.html` },
          { label: 'Swagger UI' },
        ]}
        tags={
          <Label inverted color="vattjom">
            {api.kategori}
          </Label>
        }
        title={`${api.namn} ${api.apiVersion ?? ''}`.trim()}
        lead="Interaktiv API-dokumentation, genererad ur tjänstens OpenAPI-specifikation. Anrop i produktion görs via kommunens API-plattform på api.sundsvall.se."
      />
      <PageSection>
        <div ref={container} aria-label={`Swagger UI för ${api.namn}`} />
        <noscript>
          <p>
            Swagger UI kräver JavaScript. Specifikationen kan i stället läsas som{' '}
            <Link href={`../assets/openapi/${api.slug}.yml`}>YAML</Link>.
          </p>
        </noscript>
      </PageSection>
    </SubpageChrome>
  );
}
