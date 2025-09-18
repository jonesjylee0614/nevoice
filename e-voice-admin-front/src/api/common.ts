import { defHttp } from '@/utils/http';
import type { UploadFileParams } from '/#/axios';

const apiHost = import.meta.env.VITE_API_HOST;
export function userUploadApi(
  params: UploadFileParams,
  onUploadProgress?: (progressEvent: any) => void,
  cancelToken?: any
) {
  return defHttp.uploadFile({ url: `${apiHost}/common/upload/image`, onUploadProgress, cancelToken }, params);
}
// 排序
export function tableWeigh(params: any) {
  return defHttp.post({ url: `${apiHost}/table/weigh`, params }, { errorMessageMode: 'message', isRootUrl: false });
}
export function useUploadApi(
  url: string,
  params: UploadFileParams,
  onUploadProgress?: (progressEvent: any) => void,
  cancelToken?: any
) {
  return defHttp.uploadFile({ url: `${apiHost}${url}`, onUploadProgress, cancelToken }, params);
}
