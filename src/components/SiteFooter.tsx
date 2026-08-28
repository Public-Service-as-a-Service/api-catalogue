import { Footer, Link } from '@sk-web-gui/react';
import React from 'react';

export interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
}

interface SiteFooterProps {
  title: string;
  description: React.ReactNode;
  links: FooterLink[];
}

export function SiteFooter({ title, description, links }: SiteFooterProps) {
  return (
    <Footer className="border-t border-divider bg-background-200">
      <Footer.Content>
        <div className="grid w-full gap-32 md:grid-cols-2">
          <div>
            <p className="font-header font-bold text-large mb-8 text-dark-primary">{title}</p>
            <p>{description}</p>
          </div>
          <div>
            <p className="font-header font-bold text-large mb-8 text-dark-primary">Länkar</p>
            <Footer.List>
              {links.map((link) => (
                <Footer.ListItem key={link.href}>
                  <Link href={link.href} external={link.external}>
                    {link.label}
                  </Link>
                </Footer.ListItem>
              ))}
            </Footer.List>
          </div>
        </div>
      </Footer.Content>
    </Footer>
  );
}
