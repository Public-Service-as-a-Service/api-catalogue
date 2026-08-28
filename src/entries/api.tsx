import React from 'react';
import { createRoot } from 'react-dom/client';
import { AppShell } from '../components/AppShell';
import { ApiPage, type ApiPageData } from '../pages/ApiPage';
import { readPageData } from '../types';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppShell>
      <ApiPage data={readPageData<ApiPageData>()} />
    </AppShell>
  </React.StrictMode>,
);
