// 会议状态
export enum MeetingStatus {
  PENDING = 0,    // 待开始
  ONGOING = 1,    // 进行中
  ENDED = 2       // 已结束
}

// 总结状态
export enum SummaryStatus {
  NONE = 0,       // 未生成
  GENERATING = 1, // 生成中
  DONE = 2        // 已完成
}

// 会议列表项
export interface Meeting {
  id: number
  title: string
  hostName: string
  status: MeetingStatus
  summaryStatus: SummaryStatus
  dialogCount: number
  tagList: string[]
  startTime: string
  endTime: string
  createdAt: string
  updatedAt: string
}

// 会议对话
export interface MeetingDialog {
  id: number
  seq: number
  speakerId: number
  speakerName: string
  speakerRole: string
  recognized: boolean
  recognitionNote: string
  text: string
  audioPath: string
  speakTime: string
  startOffset?: number
  endOffset?: number
}

// 会议详情
export interface MeetingDetail extends Meeting {
  description: string
  dialogs: MeetingDialog[]
  summary: string
  participants: Participant[]
}

// 参会人员
export interface Participant {
  userId: number
  userName: string
  department: string
  role: string
}

// 分页参数
export interface PageParams {
  page: number
  pageSize: number
}

// 分页响应
export interface PageResult<T> {
  items: T[]
  page: number
  pageSize: number
  total: number
}

// 创建会议参数
export interface CreateMeetingParams {
  title?: string
  description?: string
  startTime?: string
  endTime?: string
  tagList?: string[]
}

// 指定发言人参数
export interface AssignSpeakerParams {
  dialogId: number
  speakerId: number
  speakerName: string
  speakerRole: string
}

// 会议列表查询参数
export interface MeetingQueryParams extends PageParams {
  title?: string
  hostName?: string
  status?: MeetingStatus
  createdTime?: string
}
