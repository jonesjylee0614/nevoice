import {join} from 'lodash';
import {defHttp} from '@/utils/http';

const Api = {
  getList: '{{ .modPath }}/get_list',
  getContent: '{{ .modPath }}/get_content',
  save: '{{ .modPath }}/save',
  upStatus: '{{ .modPath }}/upStatus',
  del: '{{ .modPath }}/del'
};

// 列表数据
export function getList(params: any) {
  if (params.createdTime) {
    params.createdTime = join(params.createdTime);
  }
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'none' });
}
// 获取内容
export function getContent(params: object) {
  return defHttp.get({ url: Api.getContent, params }, { errorMessageMode: 'none' });
}
// 提交数据
export function save(params: object) {
  return defHttp.post({ url: Api.save, params }, { errorMessageMode: 'message' });
}
// 更新状态
export function upStatus(params: object) {
  return defHttp.post({ url: Api.upStatus, params }, { errorMessageMode: 'message' });
}
// 删除数据
export function del(params: object) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}
// 数据类型
export interface DataItem {
  id: number;
  name: string;
}
