import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Forward API calls to the Flask backend during `npm run dev`
    proxy: {
      '/api': 'http://127.0.0.1:5000',
    },
  },
})
