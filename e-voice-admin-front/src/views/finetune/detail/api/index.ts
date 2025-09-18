import { defHttp } from '@/utils/http';
export const Api = {
  getList: '/finetune/detail/get_list',
  getCate: '/finetune/detail/get_cate',
  update: '/finetune/detail/update',
  uploadAdd: '/finetune/detail/uploadAdd',
  upStatus: '/finetune/detail/upStatus',
  del: '/finetune/detail/del'
};

// 列表数据
export function getList(params: any) {
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'none' });
}
// 列表选项数据
export function getCate(params: object) {
  return defHttp.get({ url: Api.getCate, params }, { errorMessageMode: 'none' });
}
// 提交数据
export function update(params: object) {
  return defHttp.post({ url: Api.update, params }, { errorMessageMode: 'message' });
}
export function uploadAdd(params: object) {
  return defHttp.post({ url: Api.uploadAdd, params }, { errorMessageMode: 'message' });
}
// 更新状态
export function upStatus(params: object) {
  return defHttp.post({ url: Api.upStatus, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function del(params: object) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}
/** 数据类型 */
export interface DataItem {
  id: number;
  name: string;
}
