import { defHttp } from '@/utils/http';

export const Api = {
  getList: '/meeting/mdt/get_list',
  getDetail: '/meeting/mdt/get_detail',
  save: '/meeting/mdt/save',
  update: '/meeting/mdt/update',
  del: '/meeting/mdt/del',
  start: '/meeting/mdt/startMeeting',
  end: '/meeting/mdt/endMeeting',
  getDialogs: '/meeting/mdt/getDialogs',
  saveDialog: '/meeting/mdt/saveDialog',
  updateDialog: '/meeting/mdt/update_dialog',
  assignSpeaker: '/meeting/mdt/assignSpeaker',
  generateSummary: '/meeting/mdt/generateSummary',
  getSummaryStatus: '/meeting/mdt/getSummaryStatus'
};

// 获取会议列表
export function getList(params: any) {
  if (params.createdTime && params.createdTime.length > 0) {
    params.createdTime = params.createdTime.join(',');
  }
  if (params.startTime && params.startTime.length > 0) {
    params.startTime = params.startTime.join(',');
  }
  return defHttp.get({ url: Api.getList, params }, { errorMessageMode: 'none' });
}

// 获取会议详情
export function getDetail(id: number) {
  return defHttp.get({ url: Api.getDetail, params: { id } }, { errorMessageMode: 'none' });
}

// 创建会议
export function save(params: object) {
  return defHttp.post({ url: Api.save, params }, { errorMessageMode: 'message' });
}

// 更新会议
export function update(params: object) {
  return defHttp.post({ url: Api.update, params }, { errorMessageMode: 'message' });
}

// 删除会议
export function del(params: object) {
  return defHttp.delete({ url: Api.del, params }, { errorMessageMode: 'message' });
}

// 开始会议
export function startMeeting(id: number) {
  return defHttp.post({ url: `${Api.start}?id=${id}`, params: {} }, { errorMessageMode: 'message' });
}

// 结束会议
export function endMeeting(id: number) {
  return defHttp.post({ url: `${Api.end}?id=${id}`, params: {} }, { errorMessageMode: 'message' });
}

// 获取对话列表
export function getDialogs(meetingId: number) {
  return defHttp.get({ url: Api.getDialogs, params: { meetingId } }, { errorMessageMode: 'none' });
}

// 保存对话
export function saveDialog(params: object) {
  return defHttp.post({ url: Api.saveDialog, params }, { errorMessageMode: 'none' });
}

// 更新对话文本
export function updateDialog(id: number, text: string) {
  return defHttp.post({ url: Api.updateDialog, params: { id, text } }, { errorMessageMode: 'message' });
}

// 指定发言人
export function assignSpeaker(params: object) {
  return defHttp.post({ url: Api.assignSpeaker, params }, { errorMessageMode: 'message' });
}

// 生成AI总结
export function generateSummary(id: number) {
  return defHttp.get({ url: Api.generateSummary, params: { id } }, { errorMessageMode: 'message' });
}

// 获取总结状态
export function getSummaryStatus(id: number) {
  return defHttp.get({ url: Api.getSummaryStatus, params: { id } }, { errorMessageMode: 'none' });
}

// 声纹匹配
export function matchSpeaker(params: { audio_data: string; participant_user_ids?: number[] }) {
  return defHttp.post({ url: '/meeting/mdt/matchSpeaker', params }, { errorMessageMode: 'none' });
}
