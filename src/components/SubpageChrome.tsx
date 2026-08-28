import React from 'react';
import { SiteFooter } from './SiteFooter';
import { SiteHeader } from './SiteHeader';

const menu = [
  { label: 'Om katalogen', href: '../index.html#om-katalogen' },
  { label: 'API:er', href: '../index.html#apier' },
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

/** Sidhuvud, sidfot och meny för undersidorna under api/. */
export function SubpageChrome({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SiteHeader menu={menu} homeHref="../index.html" />
      <main>{children}</main>
      <SiteFooter
        title="API-katalogen"
        description="En översikt över de API:er som körs i produktion på Sundsvalls kommuns API-plattform."
        links={footerLinks}
      />
    </>
  );
}
