import '@fontsource/raleway/400.css';
import '@fontsource/raleway/600.css';
import '@fontsource/raleway/700.css';
import '@fontsource/raleway/800.css';
import '../index.css';
import { ColorSchemeMode, GuiProvider } from '@sk-web-gui/react';
import React from 'react';

export function AppShell({ children }: { children: React.ReactNode }) {
  return <GuiProvider colorScheme={ColorSchemeMode.Light}>{children}</GuiProvider>;
}
