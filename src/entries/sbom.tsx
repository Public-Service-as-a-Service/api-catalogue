import React from 'react';
import { createRoot } from 'react-dom/client';
import { AppShell } from '../components/AppShell';
import { SbomPage, type SbomPageData } from '../pages/SbomPage';
import { readPageData } from '../types';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppShell>
      <SbomPage data={readPageData<SbomPageData>()} />
    </AppShell>
  </React.StrictMode>,
);
