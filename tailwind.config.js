import { preset } from '@sk-web-gui/core';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './ekosystemet.html',
    './src/**/*.{ts,tsx}',
    './node_modules/@sk-web-gui/*/dist/**/*.js',
  ],
  // Alla tokens (färger, typografi, avstånd) kommer från designsystemets preset.
  presets: [preset()],
};
