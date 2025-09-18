import { computed } from 'vue';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = computed<TableColumnData[]>(() => [
  {
    title: '会议名',
    dataIndex: 'name',
    slotName: 'name',
    align: 'left'
  },
  {
    title: '会议时间',
    dataIndex: 'meetingTime',
    slotName: 'meetingTime',
    align: 'center',
    width: 100
  },
  {
    title: '更新人',
    dataIndex: 'updaterName',
    slotName: 'updaterName',
    width: 200,
    align: 'center'
  },
  {
    title: '更新时间',
    dataIndex: 'updateTime',
    slotName: 'updateTime',
    width: 200,
    align: 'center'
  },
  {
    title: '操作',
    dataIndex: 'options',
    slotName: 'options',
    fixed: 'right',
    width: 200,
    align: 'center'
  }
]);

export const printsColumns = computed<TableColumnData[]>(() => [
  {
    title: 'ID',
    dataIndex: 'id',
    align: 'center',
    width: 100,
    ellipsis: true
  },
  {
    title: '文字信息',
    dataIndex: 'txt',
    align: 'left',
    ellipsis: true
  },
  {
    title: '音频试听',
    dataIndex: 'wav_path',
    slotName: 'wav_path',
    width: 100,
    align: 'center'
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    slotName: 'create_time',
    align: 'center',
    width: 180
  },
  {
    title: '操作',
    dataIndex: 'options',
    slotName: 'options',
    align: 'center',
    width: 100
  }
]);
