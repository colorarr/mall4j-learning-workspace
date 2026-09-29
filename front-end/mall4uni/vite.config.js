import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import fs from 'fs'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import h5ProdEffectPlugin from 'uni-vite-plugin-h5-prod-effect'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    uni(),
    AutoImport({
      imports: [
        'vue',
        'uni-app'
      ],
      dirs: [
        'src/utils',
        'src/wxs/**'
      ],
      dts: 'src/auto-imports.d.ts',
      eslintrc: {
        enabled: true
      }
    }),
    // 对h5 production环境打包时的特殊处理，否则uni-crazy-router在这个环境会异常
    h5ProdEffectPlugin()
  ],
  server: {
    host: true,
    port: 5173,
    open: true,
    proxy: {
      '/agent-api': {
        target: 'http://127.0.0.1:18082',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/agent-api/, '')
      }
    }
  },
  resolve: {
    alias: [
      {
        find: /^markstream-vue$/,
        replacement: fs.realpathSync(path.resolve(__dirname, 'node_modules/markstream-vue/dist/index.js'))
      },
      {
        find: '@',
        replacement: path.resolve(__dirname, 'src')
      }
    ]
  }
})
