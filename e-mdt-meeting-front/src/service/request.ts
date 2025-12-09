import axios from 'axios'
import { showFailToast, showLoadingToast, closeToast } from 'vant'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  timeout: 60000,
  baseURL: import.meta.env.MODE === 'development' ? '/api' : import.meta.env.VITE_SERVER_URL
})

// 设置默认请求头
axios.defaults.headers.post['Content-Type'] = 'application/json'

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 可以在这里添加 token
    const token = localStorage.getItem('mdt_token')
    if (token) {
      config.headers.Authorization = token
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  res => {
    closeToast()
    if (res.status === 200) {
      // 处理业务错误码
      if (res.data.code && res.data.code !== 0 && res.data.code !== 200) {
        showFailToast(res.data.message || '操作失败')
        return Promise.reject(res.data)
      }
      return Promise.resolve(res)
    }
    return Promise.reject(res)
  },
  error => {
    closeToast()
    if (error.response?.status) {
      switch (error.response.status) {
        case 401:
        case 403:
        case 4031:
        case 4032:
          // 登录失效，清除 token 并跳转登录页
          showFailToast('登录已过期，请重新登录')
          localStorage.removeItem('mdt_token')
          localStorage.removeItem('mdt_user')
          // 延迟跳转，让用户看到提示
          setTimeout(() => {
            router.replace({
              path: '/login',
              query: { redirect: router.currentRoute.value.fullPath }
            })
          }, 1000)
          break
        case 404:
          showFailToast('接口不存在')
          break
        case 500:
          showFailToast('服务器错误')
          break
        default:
          showFailToast(error.response.data?.message || '请求失败')
      }
    } else {
      showFailToast('网络错误')
    }
    return Promise.reject(error)
  }
)

// 封装 loading 请求
export const requestWithLoading = async <T>(
  promise: Promise<T>,
  message = '加载中...'
): Promise<T> => {
  showLoadingToast({
    message,
    forbidClick: true,
    loadingType: 'spinner',
    duration: 0
  })
  try {
    return await promise
  } finally {
    closeToast()
  }
}

export default request
