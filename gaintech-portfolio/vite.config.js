import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Относительные пути — надёжнее в Telegram WebView (иначе бывает чёрный экран из-за /repo/assets…).
export default defineConfig({
  plugins: [react()],
  base: './',
});
