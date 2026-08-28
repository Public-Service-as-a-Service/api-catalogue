import { readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Alla sidskal under api/ är egna ingångar; de genereras av
// scripts/generate-pages.py och renderas av React-ingångarna i src/entries/.
const apiPages = Object.fromEntries(
  readdirSync(resolve(__dirname, 'api'))
    .filter((f) => f.endsWith('.html'))
    .map((f) => [`api/${f.replace(/\.html$/, '')}`, resolve(__dirname, 'api', f)]),
);

// Relativ bas gör att bygget fungerar både på GitHub Pages
// (underkatalog) och i containern (rot).
export default defineConfig({
  base: './',
  plugins: [react()],
  build: {
    // Bundlarna läggs i static/ så att webbplatsens egna assets/ kan kopieras
    // orörd till dist/assets av byggskriptet.
    assetsDir: 'static',
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
        ...apiPages,
      },
    },
  },
});
