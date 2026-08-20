import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'fs'
import path from 'path'

// Custom plugin to serve the analytics JSON and images from the parent output folder
function serveAnalyticsAssets() {
  return {
    name: 'serve-analytics-assets',
    configureServer(server: any) {
      server.middlewares.use((req: any, res: any, next: any) => {
        const urlPath = req.url.split('?')[0];
        
        if (urlPath === '/api/analytics.json') {
          const filePath = path.resolve(import.meta.dirname, '../output/analytics.json');
          if (fs.existsSync(filePath)) {
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Access-Control-Allow-Origin', '*');
            res.setHeader('Cache-Control', 'no-store');
            res.end(fs.readFileSync(filePath));
          } else {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: "analytics.json not found" }));
          }
        } else if (urlPath === '/api/heatmap_analytics.json') {
          const filePath = path.resolve(import.meta.dirname, '../output/heatmap_analytics.json');
          if (fs.existsSync(filePath)) {
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Access-Control-Allow-Origin', '*');
            res.setHeader('Cache-Control', 'no-store');
            res.end(fs.readFileSync(filePath));
          } else {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: "heatmap_analytics.json not found" }));
          }
        } else if (urlPath === '/api/customer_heatmap.png') {
          const filePath = path.resolve(import.meta.dirname, '../output/customer_heatmap.png');
          if (fs.existsSync(filePath)) {
            res.setHeader('Content-Type', 'image/png');
            res.setHeader('Access-Control-Allow-Origin', '*');
            res.setHeader('Cache-Control', 'no-store');
            res.end(fs.readFileSync(filePath));
          } else {
            res.statusCode = 404;
            res.end("Not found");
          }
        } else {
          next();
        }
      });
    }
  }
}

export default defineConfig({
  plugins: [react(), tailwindcss(), serveAnalyticsAssets()],
})
