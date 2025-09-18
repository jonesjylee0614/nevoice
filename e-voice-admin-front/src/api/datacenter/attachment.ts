import { join } from 'lodash';
import { defHttp } from '@/utils/http';
const Api = {
  getList: '/datacenter/attachment/get_list',
  getPictureCate: '/datacenter/attachment/get_pictureCate',
  getMyFiles: '/datacenter/attachment/get_myFiles',
  getPicture: '/datacenter/attachment/get_picture',
  getContent: '/datacenter/attachment/get_content',
  saveFile: '/datacenter/attachment/save',
  upImgPid: '/datacenter/attachment/upImgPid',
  delFile: '/datacenter/attachment/del'
};

// 列表数据
export function getList(params: any) {
  if (params.createdTime) {
    params.createdTime = join(params.createdTime);
  }
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'message' });
}
// 获取我的附件
export function getMyFiles(params: any) {
  return defHttp.get({ url: Api.getMyFiles, params }, { errorMessageMode: 'message' });
}
// 获取图片库
export function getPictureCate(params: any) {
  return defHttp.get({ url: Api.getPictureCate, params }, { errorMessageMode: 'message' });
}
// 获取图片库
export function get_picture(params: any) {
  return defHttp.get({ url: Api.getPicture, params }, { errorMessageMode: 'message' });
}
// 获取内容
export function getContent(params: any) {
  return defHttp.get({ url: Api.getContent, params }, { errorMessageMode: 'message' });
}
// 提交数据
export function saveFile(params: any) {
  return defHttp.post({ url: Api.saveFile, params }, { errorMessageMode: 'message' });
}
// 更新文件夹
export function upImgPid(params: any) {
  return defHttp.post({ url: Api.upImgPid, params }, { errorMessageMode: 'message' });
}
// 删除文件
export function delFile(params: any) {
  return defHttp.delete({ url: Api.delFile, params }, { errorMessageMode: 'message' });
}

/** 数据类型 */
export interface DataItem {
  id: number;
  name: string;
}
// 图片类型
export interface PictureItem {
  id: number;
  type: number;
  title: string;
  url: string;
  cover_url: string;
}
export interface CateItem {
  id: number;
  type: number;
  name: string;
}
export interface PictureItem {
  id: number;
  type: number;
  title: string;
  url: string;
}
export interface FileItem {
  id: number;
  pid: number;
  type: number;
  title: string;
  url: string;
  storage: string;
  cover_url: string;
}
