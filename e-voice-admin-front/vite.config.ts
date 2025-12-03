import { resolve } from 'node:path';
import type { UserConfig } from 'vite';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import progress from 'vite-plugin-progress';
import { CodeInspectorPlugin } from 'code-inspector-plugin';
import svgLoader from 'vite-svg-loader';
import configArcoResolverPlugin from './config/plugin/arcoResolver';
import { themeColor } from './src/config/settings.json';

export default defineConfig(config => {
  const timestamp = new Date().getTime();
  return {
    // eslint-disable-next-line n/prefer-global/process
    base: './',
    plugins: [
      vue(),
      vueJsx(),
      svgLoader({ svgoConfig: {} }),
      CodeInspectorPlugin({
        bundler: 'vite',
        editor: 'idea'
      }),

      progress(),
      // configCompressPlugin('gzip'),
      ...configArcoResolverPlugin()
    ],
    resolve: {
      alias: [
        {
          find: '@',
          replacement: resolve(__dirname, './src')
        },
        {
          find: '/@',
          replacement: resolve(__dirname, './src')
        },
        {
          find: 'assets',
          replacement: resolve(__dirname, './src/assets')
        },
        {
          find: 'vue-i18n',
          replacement: 'vue-i18n/dist/vue-i18n.cjs.js' // Resolve the i18n warning issue
        },
        {
          find: 'vue',
          replacement: 'vue/dist/vue.esm-bundler.js' // compile template
        }
      ],
      extensions: ['.ts', '.js']
    },
    define: {
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: true,
      'process.env': {}
    },
    css: {
      preprocessorOptions: {
        less: {
          modifyVars: {
            hack: `true; @import (reference) "${resolve('src/assets/style/breakpoint.less')}";`,
            'arcoblue-6': themeColor // #165DFF
          },
          javascriptEnabled: true
        }
      }
    },
    server: {
      open: false,
      fs: {
        strict: true
      },
      host: true,
      port: 9106,
      proxy: {
        '/resource': {
          target: 'http://localhost:8108/resource', // 代理的地址
          changeOrigin: true,
          rewrite: path => path.replace(/^\/resource/, '') // 这里的/需要转义
        },
        '/api': {
          target: 'http://localhost:8108/', // 代理的地址
          changeOrigin: true,
          rewrite: path => path.replace(/^\/api/, '') // 这里的/需要转义
        }
      },
      allowedHosts: ['xnng.yfqwl.com', 'evoicefront.xnng.yfqwl.com'] // 允许 xnng.yfqwl.com 主机
    },
    build: {
      reportCompressedSize: false,
      sourcemap: false,
      commonjsOptions: {
        ignoreTryCatch: false
      },
      // chunks 大小限制
      chunkSizeWarningLimit: 2000,
      // 删除文件中console、debugger等调试用的多余代码
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      },
      rollupOptions: {
        output: {
          entryFileNames: `assets/[name]-[hash].${timestamp}.js`,
          chunkFileNames: `assets/[name]-[hash].${timestamp}.js`,
          assetFileNames: `assets/[name]-[hash].${timestamp}.[ext]`,
          advancedChunks: {
            groups: [
              {
                name: 'echarts',
                test: /(echarts|vue-echarts)/i
              },
              {
                name: 'monaco',
                test: /(monaco-editor)/i
              },
              {
                name: 'arco',
                test: /(@arco-design\/web-vue)/i
              }
            ]
          }
        }
      }
    }
  } as UserConfig;
});
