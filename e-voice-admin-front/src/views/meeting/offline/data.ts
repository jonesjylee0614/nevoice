import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = [
  {
    title: '会议名',
    dataIndex: 'name',
    align: 'left'
  },
  {
    title: '会议时间',
    dataIndex: 'meetingTime',
    align: 'left',
    width: 200
  },
  {
    title: '更新人',
    dataIndex: 'updaterName',
    align: 'left',
    width: 150
  },
  {
    title: '更新时间',
    dataIndex: 'updateTime',
    align: 'left',
    width: 200
  },
  {
    title: '操作',
    dataIndex: 'operations',
    slotName: 'operations',
    align: 'center',
    fixed: 'right',
    width: 200
  }
] as TableColumnData[];

export const detailColumns = [
  {
    title: '序号',
    dataIndex: 'sort',
    align: 'left',
    width: 80
  },
  {
    title: '说话人',
    dataIndex: 'spkUserName',
    slotName: 'spkUserName',
    align: 'left',
    width: 100
  },
  {
    title: '说话内容',
    dataIndex: 'text',
    align: 'left'
  },
  {
    title: '时间戳',
    dataIndex: 'spkTime',
    align: 'left',
    width: 200
  },
  {
    title: '训练状态',
    dataIndex: 'trainStatus',
    slotName: 'trainStatus',
    align: 'left',
    width: 100
  },
  {
    title: '操作',
    dataIndex: 'operations',
    slotName: 'operations',
    align: 'center',
    fixed: 'right',
    width: 200
  }
] as TableColumnData[];
