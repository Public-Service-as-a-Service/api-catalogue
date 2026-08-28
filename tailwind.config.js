import { preset } from '@sk-web-gui/core';

/** @type {import('tailwindcss').Config} */
export default {
  // Webbplatsen renderas alltid i ljust läge: mörkt läge aktiveras bara av en
  // klass (som aldrig sätts), inte av webbläsarens prefers-color-scheme.
  darkMode: 'class',
  content: [
    './index.html',
    './ekosystemet.html',
    './src/**/*.{ts,tsx}',
    './node_modules/@sk-web-gui/*/dist/**/*.js',
  ],
  // Alla tokens (färger, typografi, avstånd) kommer från designsystemets preset.
  presets: [preset()],
};
