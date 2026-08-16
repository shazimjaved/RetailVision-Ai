import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'fs'
import path from 'path'

// Custom plugin to serve the analytics.json from the parent output folder
function serveAnalyticsJson() {
  return {
    name: 'serve-analytics-json',
    configureServer(server: any) {
      server.middlewares.use('/api/analytics.json', (_req: any, res: any) => {
        const filePath = path.resolve(import.meta.dirname, '../output/analytics.json')
        if (fs.existsSync(filePath)) {
          res.setHeader('Content-Type', 'application/json')
          res.setHeader('Access-Control-Allow-Origin', '*')
          // Disable caching so refresh always gets the latest
          res.setHeader('Cache-Control', 'no-store')
          res.end(fs.readFileSync(filePath))
        } else {
          res.statusCode = 404
          res.end(JSON.stringify({ error: "analytics.json not found" }))
        }
      })
    }
  }
}

export default defineConfig({
  plugins: [react(), tailwindcss(), serveAnalyticsJson()],
})
