import { defHttp } from '@/utils/http';
const Api = {
  getEmail: '/datacenter/configuration/get_email',
  saveEmail: '/datacenter/configuration/saveEmail'
};

// 列表数据
export function getEmail(params: any) {
  return defHttp.get({ url: Api.getEmail, params }, { errorMessageMode: 'message' });
}
// 提交数据
export function saveEmail(params: any) {
  return defHttp.post({ url: Api.saveEmail, params }, { errorMessageMode: 'message' });
}
/** 数据类型 */
export interface menuItem {
  id: number;
  title: string;
}
