import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  build: {
    rolldownOptions: {
      output: {
        // Libraries change far less often than our code, so they cache separately.
        codeSplitting: {
          groups: [
            { name: 'map', test: /node_modules[\\/](leaflet|react-leaflet|@react-leaflet)[\\/]/ },
            { name: 'ui', test: /node_modules[\\/](@mui|@emotion|@popperjs|react-transition-group)[\\/]/ },
            { name: 'react', test: /node_modules[\\/](react|react-dom|scheduler)[\\/]/ },
          ],
        },
      },
    },
  },
})
