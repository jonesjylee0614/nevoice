import { defHttp } from '@/utils/http';
// 类型
export interface LoginData {
  username: string;
  password: string;
}
const Api = {
  getList: '/system/account/get_list',
  getRole: '/system/account/get_role',
  save: '/system/account/save',
  Isaccountexist: '/system/account/isaccountexist',
  upStatus: '/system/account/upStatus',
  del: '/system/account/del'
};

// 数据列表
export function getList(params: any) {
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'message' });
}
// 选择角色
export function getRole() {
  return defHttp.get({ url: Api.getRole }, { errorMessageMode: 'message' });
}
// 提交菜单
export function save(params: any) {
  return defHttp.post({ url: Api.save, params }, { errorMessageMode: 'message' });
}
// 判断账号是否已经存在
export function isAccountexist(params: any) {
  return defHttp.post({ url: Api.Isaccountexist, params }, { errorMessageMode: 'message', isTransformResponse: false });
}
// 更新状态
export function upStatus(params: any) {
  return defHttp.post({ url: Api.upStatus, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function del(params: any) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}
/** 数据类型 */
export interface DataItem {
  id: number;
  pid: number;
  locale: string;
  title: string;
}
