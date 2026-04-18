import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// GitHub Pages project URL: /<repo>/
export default defineConfig({
  plugins: [react()],
  base: '/gaintech-telegram-bot/',
});
