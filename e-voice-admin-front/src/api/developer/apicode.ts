import { defHttp } from '@/utils/http';
const Api = {
  installcode: '/developer/apicode/installcode',
  uninstallcode: '/developer/apicode/uninstallcode',
  removeFile: '/developer/apicode/removeFile'
};
// 生成接口代码
export function installcode(params: any) {
  return defHttp.post({ url: Api.installcode, params }, { errorMessageMode: 'message' });
}
// 卸载接口代码
export function uninstallcode(params: any) {
  return defHttp.post({ url: Api.uninstallcode, params }, { errorMessageMode: 'message' });
}
// 卸载接口代码
export function removeFile(params: any) {
  return defHttp.post({ url: Api.removeFile, params }, { errorMessageMode: 'message' });
}
