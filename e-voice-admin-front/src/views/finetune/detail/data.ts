import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = [
  {
    title: '语料文本',
    dataIndex: 'text',
    align: 'left'
  },
  {
    title: '更新时间',
    dataIndex: 'updateTime',
    align: 'left'
  },
  {
    title: '更新人名称',
    dataIndex: 'updaterName',
    align: 'left'
  },
  {
    title: '操作',
    dataIndex: 'operations',
    slotName: 'operations',
    align: 'center'
  }
] as TableColumnData[];
