import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    return {
      build: {
        outDir: 'dist',
      },
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      define: {
        'process.env': {}
      },
      plugins: [react()],
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
