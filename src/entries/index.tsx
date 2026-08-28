import React from 'react';
import { createRoot } from 'react-dom/client';
import { AppShell } from '../components/AppShell';
import { IndexPage } from '../pages/IndexPage';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppShell>
      <IndexPage />
    </AppShell>
  </React.StrictMode>,
);
