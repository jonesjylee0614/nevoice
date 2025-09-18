import md5 from 'md5';
import { defHttp } from '@/utils/http';
// 类型
export interface LoginData {
  username: string;
  password: string;
  secret: string;
}
const Api = {
  // 用户
  Login: '/user/login ',
  registerUser: '/user/registerUser ',
  Logout: '/user/logout',
  getCode: '/user/get_code',
  resetPassword: '/user/resetPassword',
  GetUserInfo: '/user/get_userinfo',
  GetMenu: '/user/account/get_menu',
  getlogininfo: '/user/get_logininfo'
};
// 登录
export function login(params: any) {
  return defHttp.post({ url: Api.Login, params }, { errorMessageMode: 'message' });
}
// 重置密码
export function resetPassword(params: LoginData) {
  params = { ...params, password: md5(params.password) }; // 加密推送
  return defHttp.post({ url: Api.resetPassword, params }, { errorMessageMode: 'message' });
}
// 退出登录
export function logout() {
  return defHttp.post({ url: Api.Logout }, { errorMessageMode: 'message' });
}
// 获取用信息
export function getUserInfo() {
  return defHttp.get({ url: Api.GetUserInfo }, { errorMessageMode: 'message' });
}
// 获取验证码
export function getCode(params: any) {
  return defHttp.get({ url: Api.getCode, params }, { errorMessageMode: 'message' });
}

// 获取后台菜单
export function getMenuList() {
  return defHttp.get({ url: Api.GetMenu }, { errorMessageMode: 'message' });
}

// 获取登录信息
export function getlogininfo(params: any) {
  return defHttp.get({ url: Api.getlogininfo, params }, { errorMessageMode: 'message' });
}
