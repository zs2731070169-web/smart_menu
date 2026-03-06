import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/smart/menu': {
        target: 'http://localhost:8000', // 后端接口地址
        changeOrigin: true, // 允许跨域
      }
    },
  },
})