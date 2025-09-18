import { defHttp } from '@/utils/http';
export const Api = {
  getUserList: '/voice/print/getUserList',
  getUserPrints: '/voice/print/getUserPrints',
  saveUserPrint: '/voice/print/saveUserPrint',
  userIdentify: '/voice/print/identify',
  delUserPrint: '/voice/print/del'
};

// 列表数据
export function getUserList(params: any) {
  return defHttp.get({ url: Api.getUserList, params }, { errorMessageMode: 'message' });
}
// 获取内容
export function getUserPrints(params: object) {
  return defHttp.get({ url: Api.getUserPrints, params }, { errorMessageMode: 'message' });
}
// 提交数据
export function saveUserPrint(params: object) {
  return defHttp.post(
    { url: Api.saveUserPrint, params, headers: { 'Content-Type': 'multipart/form-data' } },
    { errorMessageMode: 'message' }
  );
}
// 声纹鉴定
export function userIdentify(params: object) {
  return defHttp.post(
    { url: Api.userIdentify, params, headers: { 'Content-Type': 'multipart/form-data' } },
    { errorMessageMode: 'message' }
  );
}
// 删除数据
export function delUserPrint(params: object) {
  return defHttp.delete({ url: Api.delUserPrint, params }, { errorMessageMode: 'message' });
}
