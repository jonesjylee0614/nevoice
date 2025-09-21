import { defHttp } from '@/utils/http';
export const Api = {
  getList: '/finetune/task/get_list',
  getCate: '/finetune/task/get_cate',
  save: '/finetune/task/save',
  start: '/finetune/task/start',
  del: '/finetune/task/del',
  log: '/finetune/task/log',
  testModel: '/finetune/task/testModel',
  adoptModel: '/finetune/task/adoptModel'
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
export function save(params: object) {
  return defHttp.post({ url: Api.save, params }, { errorMessageMode: 'message' });
}
// 更新状态
export function start(params: object) {
  return defHttp.post({ url: Api.start, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function del(params: object) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function fetchLog(params: object) {
  return defHttp.post({ url: Api.log, params }, { errorMessageMode: 'message' });
}
// 测试模型
export function testModel(params: object) {
  return defHttp.post(
    { url: Api.testModel, params, headers: { 'Content-Type': 'multipart/form-data' } },
    { errorMessageMode: 'message' }
  );
}
export function adoptModel(params: object) {
  return defHttp.post({ url: Api.adoptModel, params }, { errorMessageMode: 'message' });
}
/** 数据类型 */
export interface DataItem {
  id: number;
  name: string;
}
