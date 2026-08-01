import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The build output is written to ../static and committed to git, so Render's
// build command stays Python-only. See PLAN.md R3.
//
// In dev, /api is proxied to uvicorn on :8000 so the browser only ever talks to
// one origin — same as production, where FastAPI serves both. CORS never applies.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
