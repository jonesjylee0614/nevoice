import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from 'unplugin-vue-components/resolvers'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router'],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [VantResolver()]
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 9598,
    proxy: {
      '/api': {
        target: 'http://localhost:8108',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/data': {
        target: 'http://localhost:8210',
        changeOrigin: true
      }
    },
    allowedHosts: ['localhost', 'mdt.xnng.yfqwl.com', 'xnng.yfqwl.com'] // 允许外网域名访问
  }
})
