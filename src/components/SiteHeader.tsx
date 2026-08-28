import { Header, Link, Logo } from '@sk-web-gui/react';

export interface MenuItem {
  label: string;
  href: string;
  external?: boolean;
}

export function SiteHeader({ menu, homeHref }: { menu: MenuItem[]; homeHref: string }) {
  return (
    <Header
      logo={
        <Link
          href={homeHref}
          className="no-underline"
          aria-label="API-katalogen Sundsvalls kommun. Gå till startsidan."
        >
          <Logo variant="service" title="API-katalogen" subtitle="Sundsvalls kommun" />
        </Link>
      }
      mainMenu={
        <nav aria-label="Huvudmeny" className="flex flex-wrap items-center gap-x-24 gap-y-8 py-12">
          {menu.map((item) => (
            <Link key={item.href} href={item.href} external={item.external} variant="tertiary">
              {item.label}
            </Link>
          ))}
        </nav>
      }
    />
  );
}
