import { defHttp } from '@/utils/http';
const Api = {
  getConfig: '/datacenter/common_config/get_config',
  saveConfig: '/datacenter/common_config/saveConfig'
};

// 列表数据
export function getConfig(params: any) {
  return defHttp.get({ url: Api.getConfig, params }, { errorMessageMode: 'message' });
}
// 提交数据
export function saveConfig(params: any) {
  return defHttp.post({ url: Api.saveConfig, params }, { errorMessageMode: 'message' });
}
/** 数据类型 */
export interface menuItem {
  id: number;
  title: string;
}
