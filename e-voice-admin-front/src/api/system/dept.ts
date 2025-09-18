import { defHttp } from '@/utils/http';
// 类型
export interface LoginData {
  username: string;
  password: string;
}
const Api = {
  getList: '/system/dept/get_list',
  getParent: '/system/dept/get_parent',
  save: '/system/dept/save',
  upStatus: '/system/dept/upStatus',
  del: '/system/dept/del'
};

// 列表数据
export function getList(params: any) {
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'message' });
}
// 选择数据
export function getParent() {
  return defHttp.get({ url: Api.getParent }, { errorMessageMode: 'message' });
}
// 提交数据
export function save(params: any) {
  return defHttp.post({ url: Api.save, params }, { errorMessageMode: 'message' });
}
// 更新状态
export function upStatus(params: any) {
  return defHttp.post({ url: Api.upStatus, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function del(params: any) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}
