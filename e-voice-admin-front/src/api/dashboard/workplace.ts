import { defHttp } from '@/utils/http';
const Api = {
  saveQuick: '/dashboard/workplace/saveQuick',
  getQuick: '/dashboard/workplace/get_quick',
  delQuick: '/dashboard/workplace/del_quick'
};

// 提交快捷操作数据
export function saveQuick(params: any) {
  return defHttp.post({ url: Api.saveQuick, params }, { errorMessageMode: 'message' });
}
// 获取快捷操作
export function getQuick(params: any) {
  return defHttp.get<QuickItem[]>({ url: Api.getQuick, params }, { errorMessageMode: 'message' });
}
// 删除快捷操作
export function delQuick(params: any) {
  return defHttp.delete({ url: Api.delQuick, params }, { errorMessageMode: 'message' });
}
// 快捷类型
export interface QuickItem {
  id: number;
  name: string;
  icon: string;
  path_url: string;
  is_common: number;
  type: number;
}
