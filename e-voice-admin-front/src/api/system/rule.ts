import { defHttp } from '@/utils/http';
// 类型
export interface LoginData {
  username: string;
  password: string;
}
const Api = {
  getList: '/system/rule/get_list',
  getParent: '/system/rule/get_parent',
  save: '/system/rule/save',
  upStatus: '/system/rule/upStatus',
  upOrder: '/system/rule/upOrder',
  del: '/system/rule/del'
};

// 菜单选择菜单
export function getList(params: any) {
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'message' });
}
// 菜单选择菜单
export function getParent(params: any) {
  return defHttp.get({ url: Api.getParent, params }, { errorMessageMode: 'message' });
}
// 提交菜单
export function save(params: any) {
  return defHttp.post({ url: Api.save, params }, { errorMessageMode: 'message' });
}
// 更新状态
export function upStatus(params: any) {
  return defHttp.post({ url: Api.upStatus, params }, { errorMessageMode: 'message' });
}
export function upOrder(params: any) {
  return defHttp.post({ url: Api.upOrder, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function del(params: any) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}
/** 数据类型 */
export interface RuleItem {
  id: number;
  pid: number;
  locale: string;
  title: string;
  routePath: string;
}
