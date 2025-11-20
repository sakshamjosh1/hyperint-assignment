// frontend/vite.config.js  (CommonJS version — safe on Windows/Node)
const { defineConfig } = require('vite')
const react = require('@vitejs/plugin-react')

// Using CommonJS module.exports avoids needing "type":"module" in package.json
module.exports = defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
