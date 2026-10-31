import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://adineo-cmd.github.io',
  base: '/longevity-protocol/',
  output: 'static',
  integrations: [sitemap()],
  prefetch: { prefetchAll: true },
  compressHTML: true,
});
