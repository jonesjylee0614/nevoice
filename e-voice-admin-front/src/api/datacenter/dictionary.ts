import { defHttp } from '@/utils/http';
const Api = {
  getList: '/datacenter/dictionary/get_list',
  getContent: '/datacenter/dictionary/get_content',
  save: '/datacenter/dictionary/save',
  upStatus: '/datacenter/dictionary/upStatus',
  del: '/datacenter/dictionary/del'
};

// 列表数据
export function getList(params: any) {
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'message' });
}
// 获取内容
export function getContent(params: any) {
  return defHttp.get({ url: Api.getContent, params }, { errorMessageMode: 'message' });
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
/** 数据类型 */
export interface DataItem {
  id: number;
  name: string;
}
