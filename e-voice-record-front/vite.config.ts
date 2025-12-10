import {defineConfig, loadEnv, UserConfig} from 'vite'
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import progress from 'vite-plugin-progress';
import {CodeInspectorPlugin} from 'code-inspector-plugin';
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import {VantResolver} from "@vant/auto-import-resolver";
import {resolve} from 'path';
import process from "node:process";

const pathResolve = (dir: string): any => {
    return resolve(__dirname, '.', dir);
};

// https://cn.vitejs.dev/guide/
export default defineConfig(configEnv => {
    const timeStamp = new Date().getTime() // 添加时间戳
    const viteEnv = loadEnv(configEnv.mode, process.cwd()) as unknown as Env.ImportMeta;

    return {
        base: viteEnv.VITE_BASE_URL,
        resolve: {
            alias: {
                '@': pathResolve('src/'),
            },
        },
        server: {
            host: '0.0.0.0',
            port: 9599,
            open: true,
            proxy: {
                '/api': {
                    target: viteEnv.VITE_SERVER_URL,
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/api/, ""),
                },
            },
            fs: {
                cachedChecks: false
            },
            allowedHosts: ['localhost', 'evoice.xnng.yfqwl.com', 'record.xnng.yfqwl.com', 'xnng.yfqwl.com'] // 允许外网域名访问
        },
        preview: {
            port: 9725
        },
        plugins: [
            vue({
                script: {
                    defineModel: true
                }
            }),
            AutoImport({
                imports: [
                    'vue',
                    'vue-router',
                    'pinia',
                ],
                dts: 'src/typings/auto-imports.d.ts',
                resolvers: [VantResolver()],
            }),
            Components({
                dts: 'src/typings/components.d.ts',
                resolvers: [VantResolver()],
            }),
            vueJsx(),
            progress(),
            CodeInspectorPlugin({
                bundler: 'vite',
                editor: 'idea'
            })
        ],
        build: {
            sourcemap: false,
            // chunks 大小限制
            chunkSizeWarningLimit: 2000,
            // 删除文件中console、debugger等调试用的多余代码
            terserOptions: {
                compress: {
                    drop_console: true,
                    drop_debugger: true
                }
            },
            // 自定义底层的 Rollup 打包配置
            rolldownOptions: {
                output: {
                    // 将静态文件进行分类存放 并添加时间戳 每次打包文件资源不同
                    chunkFileNames: `assets/js/[hash].${timeStamp}.js`,
                    entryFileNames: `assets/js/[hash].${timeStamp}.js`,
                    assetFileNames: `assets/[ext]/[hash].${timeStamp}.[ext]`
                }
            }
        },
    } as UserConfig
})
