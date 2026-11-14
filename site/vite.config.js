import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The site is served from https://<user>.github.io/open-finance-toolkit/,
// so every asset path must start with that folder name.
export default defineConfig({
  base: '/open-finance-toolkit/',
  plugins: [react()],
});
