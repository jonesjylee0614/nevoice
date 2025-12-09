import request from '@/service/request'
import type { 
  Meeting, 
  MeetingDetail, 
  PageResult, 
  MeetingQueryParams, 
  CreateMeetingParams,
  AssignSpeakerParams,
  Participant
} from './types'

const Api = {
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
  getSummaryStatus: '/meeting/mdt/getSummaryStatus',
  clearDialogs: '/meeting/mdt/clearDialogs',
  getStaffList: '/meeting/mdt/getStaffList'
}

// 获取会议列表
export function getList(params: MeetingQueryParams) {
  // 处理时间范围
  const query: Record<string, unknown> = { ...params }
  if (params.createdTime) {
    query.createdTime = params.createdTime
  }
  return request.get<{ data: PageResult<Meeting> }>(Api.getList, { params: query })
}

// 获取会议详情
export function getDetail(id: number) {
  return request.get<{ data: MeetingDetail }>(Api.getDetail, { params: { id } })
}

// 创建会议
export function createMeeting(params: CreateMeetingParams) {
  return request.post<{ data: { id: number } }>(Api.save, params)
}

// 更新会议
export function updateMeeting(params: CreateMeetingParams & { id: number }) {
  return request.post<{ data: void }>(Api.update, params)
}

// 删除会议
export function deleteMeeting(ids: number[]) {
  return request.delete<{ data: void }>(Api.del, { data: { ids } })
}

// 开始会议
export function startMeeting(id: number) {
  return request.post<{ data: void }>(`${Api.start}?id=${id}`)
}

// 结束会议
export function endMeeting(id: number) {
  return request.post<{ data: void }>(`${Api.end}?id=${id}`)
}

// 更新对话文本
export function updateDialogText(id: number, text: string) {
  return request.post<{ data: void }>(Api.updateDialog, { id, text })
}

// 指定发言人
export function assignSpeaker(params: AssignSpeakerParams) {
  return request.post<{ data: void }>(Api.assignSpeaker, params)
}

// 生成AI总结
export function generateSummary(id: number) {
  return request.post<{ data: void }>(`${Api.generateSummary}?id=${id}`)
}

// 获取总结状态
export function getSummaryStatus(id: number) {
  return request.get<{ data: { status: number; summary: string } }>(
    Api.getSummaryStatus, 
    { params: { id } }
  )
}

// 清空对话记录
export function clearDialogs(meetingId: number) {
  return request.post<{ data: { deletedCount: number } }>(
    `${Api.clearDialogs}?meetingId=${meetingId}`
  )
}

// 获取人员列表
export function getStaffList() {
  return request.get<{ data: Participant[] }>(Api.getStaffList)
}

// 保存对话记录
export function saveDialog(params: Partial<MeetingDialog> & { meetingId: number }) {
  return request.post<{ data: { id: number } }>(Api.saveDialog, params)
}