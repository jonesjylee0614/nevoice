import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
import { MeetingStatus, RecognizedStatus, SummaryStatus } from './api/types';

// 会议列表表格列配置
export const columns: TableColumnData[] = [
  {
    title: '会议标题',
    dataIndex: 'title',
    align: 'left',
    ellipsis: true,
    tooltip: true
  },
  {
    title: '主持人',
    dataIndex: 'hostName',
    align: 'left',
    width: 120
  },
  {
    title: '开始时间',
    dataIndex: 'startTime',
    align: 'left',
    width: 180
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    align: 'center',
    width: 100
  },
  {
    title: '对话数',
    dataIndex: 'dialogCount',
    align: 'center',
    width: 80
  },
  {
    title: '总结状态',
    dataIndex: 'summaryStatus',
    slotName: 'summaryStatus',
    align: 'center',
    width: 100
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
    align: 'left',
    width: 180
  },
  {
    title: '操作',
    dataIndex: 'operations',
    slotName: 'operations',
    align: 'center',
    fixed: 'right',
    width: 180
  }
];

// 对话列表表格列配置
export const dialogColumns: TableColumnData[] = [
  {
    title: '序号',
    dataIndex: 'seq',
    align: 'center',
    width: 60
  },
  {
    title: '发言人',
    dataIndex: 'speakerName',
    slotName: 'speakerName',
    align: 'left',
    width: 150
  },
  {
    title: '发言内容',
    dataIndex: 'text',
    align: 'left',
    ellipsis: true,
    tooltip: true
  },
  {
    title: '发言时间',
    dataIndex: 'speakTime',
    align: 'left',
    width: 180
  },
  {
    title: '识别状态',
    dataIndex: 'recognized',
    slotName: 'recognized',
    align: 'center',
    width: 120
  },
  {
    title: '操作',
    dataIndex: 'operations',
    slotName: 'operations',
    align: 'center',
    fixed: 'right',
    width: 120
  }
];

// 会议状态映射
export const meetingStatusMap: Record<MeetingStatus, { text: string; color: string }> = {
  [MeetingStatus.Pending]: { text: '待开始', color: 'gray' },
  [MeetingStatus.InProgress]: { text: '进行中', color: 'green' },
  [MeetingStatus.Ended]: { text: '已结束', color: 'blue' }
};

// 总结状态映射
export const summaryStatusMap: Record<SummaryStatus, { text: string; color: string }> = {
  [SummaryStatus.None]: { text: '未生成', color: 'gray' },
  [SummaryStatus.Generating]: { text: '生成中', color: 'orange' },
  [SummaryStatus.Done]: { text: '已生成', color: 'green' }
};

// 识别状态映射
export const recognizedStatusMap: Record<RecognizedStatus, { text: string; color: string }> = {
  [RecognizedStatus.None]: { text: '未识别', color: 'red' },
  [RecognizedStatus.Auto]: { text: '声纹识别', color: 'green' },
  [RecognizedStatus.Manual]: { text: '手动指定', color: 'blue' }
};
