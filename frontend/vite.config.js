import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/api': 'http://localhost:8200',
      '/auth': 'http://localhost:8200',
      '/webhook': 'http://localhost:8200',
      '/badge': 'http://localhost:8200',
    },
  },
})
