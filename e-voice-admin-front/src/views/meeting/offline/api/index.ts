import { defHttp } from '@/utils/http';
export const Api = {
  getList: '/meeting/offline/get_list',
  save: '/meeting/offline/save',
  update: '/meeting/offline/update',
  del: '/meeting/offline/del',
  getDetail: '/meeting/offline/getDetail',
  trainDetail: '/meeting/offline/trainDetail',
  updateDetail: '/meeting/offline/updateDetail'
};

// 列表数据
export function getList(params: any) {
  if (params.createdTime && params.createdTime.length > 0) {
    params.createdTime = params.createdTime.join(',');
  }
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'none' });
}
// 提交数据
export function update(params: object) {
  return defHttp.post({ url: Api.update, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function del(params: object) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}

// 获取会议详情
export function getDetail(params: any) {
  return defHttp.get({ url: Api.getDetail, params }, { errorMessageMode: 'none' });
}
export function updateDetail(params: any) {
  return defHttp.post({ url: Api.updateDetail, params }, { errorMessageMode: 'none' });
}
export function trainDetail(params: any) {
  return defHttp.post({ url: Api.trainDetail, params }, { errorMessageMode: 'none' });
}
