import { defineStore } from 'pinia'
import { login as loginApi, getUserInfo as getUserInfoApi, logout as logoutApi } from '@/api/auth'
import type { UserInfo, LoginParams } from '@/api/auth'

const TOKEN_KEY = 'mdt_token'
const USER_KEY = 'mdt_user'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    userInfo: JSON.parse(localStorage.getItem(USER_KEY) || 'null') as UserInfo | null,
    loading: false
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.userInfo?.name || state.userInfo?.username || '未知用户'
  },

  actions: {
    // 登录
    async login(params: LoginParams) {
      this.loading = true
      try {
        const { data } = await loginApi(params)
        const token = data.data
        this.token = token
        localStorage.setItem(TOKEN_KEY, token)
        
        // 获取用户信息
        await this.fetchUserInfo()
        
        return true
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取用户信息
    async fetchUserInfo() {
      try {
        const { data } = await getUserInfoApi()
        this.userInfo = data.data
        localStorage.setItem(USER_KEY, JSON.stringify(data.data))
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 获取用户信息失败，清除 token
        this.clearAuth()
        throw error
      }
    },

    // 退出登录
    async logout() {
      try {
        await logoutApi()
      } catch {
        // 即使退出接口失败，也清除本地状态
      } finally {
        this.clearAuth()
      }
    },

    // 清除认证信息
    clearAuth() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    }
  }
})
