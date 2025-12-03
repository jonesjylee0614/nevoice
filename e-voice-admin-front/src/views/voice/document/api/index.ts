import { defHttp } from '@/utils/http';

export const Api = {
  getList: '/voice/document/get_list',
  save: '/voice/document/save',
  delete: '/voice/document/del',
  updateStatus: '/voice/document/upStatus',
  getContent: '/voice/document/get_content'
};

// 获取列表
export function getList(params: any) {
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'message' });
}

// 保存
export function save(params: any) {
  return defHttp.post({ url: Api.save, params }, { errorMessageMode: 'message' });
}

// 删除
export function deleteDoc(params: any) {
  return defHttp.delete({ url: Api.delete, params }, { errorMessageMode: 'message' });
}

// 更新状态
export function updateStatus(params: any) {
  return defHttp.post({ url: Api.updateStatus, params }, { errorMessageMode: 'message' });
}

// 获取详情
export function getContent(params: any) {
  return defHttp.get({ url: Api.getContent, params }, { errorMessageMode: 'message' });
}
