import { defHttp } from '@/utils/http';
// 类型
const Api = {
  getTables: '/developer/devapi/get_tables'
};
// 获取数据库表
export function getTables(params: any) {
  return defHttp.get({ url: Api.getTables, params }, { errorMessageMode: 'message' });
}
/** 数据库表类型 */
export interface TableItem {
  name: string;
  title: string;
}
