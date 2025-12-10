import { defHttp } from '@/utils/http';

export const Api = {
  getList: '/voice/hotword/get_list',
  save: '/voice/hotword/save',
  delete: '/voice/hotword/del',
  updateStatus: '/voice/hotword/upStatus',
  getDetail: '/voice/hotword/get_detail',
  import: '/voice/hotword/import',
  export: '/voice/hotword/export',
  sync: '/voice/hotword/sync',
  getStats: '/voice/hotword/get_stats'
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
export function deleteHotword(params: any) {
  return defHttp.delete({ url: Api.delete, params }, { errorMessageMode: 'message' });
}

// 更新状态
export function updateStatus(params: any) {
  return defHttp.post({ url: Api.updateStatus, params }, { errorMessageMode: 'message' });
}

// 获取详情
export function getDetail(params: any) {
  return defHttp.get({ url: Api.getDetail, params }, { errorMessageMode: 'message' });
}

// 导入热词
export function importHotwords(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return defHttp.uploadFile({ url: Api.import }, { file, name: 'file' });
}

// 获取导出链接
export function getExportUrl() {
  return Api.export;
}

// 同步到文件
export function syncToFile() {
  return defHttp.post({ url: Api.sync }, { errorMessageMode: 'message' });
}

// 获取统计信息
export function getStats() {
  return defHttp.get({ url: Api.getStats }, { errorMessageMode: 'message' });
}
