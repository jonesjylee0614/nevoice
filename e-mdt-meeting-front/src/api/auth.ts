import request from '@/service/request'

const Api = {
  login: '/user/login',
  getUserInfo: '/user/get_userinfo',
  logout: '/user/logout',
  getLoginInfo: '/user/get_logininfo'
}

// 登录参数
export interface LoginParams {
  username: string
  password: string
}

// 用户信息
export interface UserInfo {
  userId: number
  username: string
  name: string
  avatar: string
  introduction: string
  nickname: string
  city: string
  company: string
  role: string
  perms: string[]
}

// 登录
export function login(params: LoginParams) {
  // 简单登录，传递占位符绕过 required 验证
  // 后端会检查 encryptStr 非空时才进行解密处理
  return request.post<{ data: string }>(Api.login, {
    username: params.username,
    password: params.password,
    encryptStr: 'plain' // 占位符，表示使用明文登录
  })
}

// 获取用户信息
export function getUserInfo() {
  return request.get<{ data: UserInfo }>(Api.getUserInfo)
}

// 退出登录
export function logout() {
  return request.post<{ data: boolean }>(Api.logout)
}

// 获取登录页面信息
export function getLoginInfo() {
  return request.get<{ data: unknown[] }>(Api.getLoginInfo)
}
