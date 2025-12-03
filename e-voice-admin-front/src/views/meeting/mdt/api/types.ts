// 会议状态
export enum MeetingStatus {
  Pending = 0, // 待开始
  InProgress = 1, // 进行中
  Ended = 2 // 已结束
}

// 总结状态
export enum SummaryStatus {
  None = 0, // 未生成
  Generating = 1, // 生成中
  Done = 2 // 已生成
}

// 识别状态
export enum RecognizedStatus {
  None = 0, // 未识别
  Auto = 1, // 声纹自动识别
  Manual = 2 // 手动指定
}

// 参会人
export interface Participant {
  userId: number;
  userName: string;
  department: string;
  role: string;
}

// 会议对话
export interface MeetingDialog {
  id: number;
  meetingId: number;
  seq: number;
  speakerId: number | null;
  speakerName: string;
  speakerRole: string;
  recognized: RecognizedStatus;
  recognitionNote: string;
  recognitionScore: number | null;
  speakTime: string;
  startOffset: number;
  endOffset: number;
  durationMs: number;
  text: string;
  audioPath: string;
  createTime: string;
}

// 会议详情
export interface MeetingDetail {
  id: number;
  title: string;
  description: string;
  hostId: number | null;
  hostName: string;
  startTime: string;
  endTime: string;
  status: MeetingStatus;
  participants: string;
  tags: string;
  summary: string;
  summaryStatus: SummaryStatus;
  audioPath: string;
  dialogCount: number;
  durationSeconds: number;
  createTime: string;
  updateTime: string;
  dialogs: MeetingDialog[];
  participantList: Participant[];
  tagList: string[];
}

// 创建会议请求
export interface CreateMeetingReq {
  title: string;
  description?: string;
  hostId?: number;
  hostName?: string;
  startTime?: string;
  endTime?: string;
  tags?: string[];
}

// 指定发言人请求
export interface AssignSpeakerReq {
  dialogId: number;
  speakerId: number;
  speakerName: string;
  speakerRole?: string;
}
