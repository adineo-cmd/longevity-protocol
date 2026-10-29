import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://longevity-protocol.example.com',
  output: 'static',
  integrations: [sitemap()],
  prefetch: { prefetchAll: true },
  compressHTML: true,
});
