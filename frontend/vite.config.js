import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  configFile: false, // Evita problemas com cache de config
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    },
    watch: {
      usePolling: true
    },
    fs: {
      strict: false
    }
  },
  cacheDir: resolve(__dirname, 'node_modules/.vite'),
  optimizeDeps: {
    force: false
  },
  clearScreen: false
})

