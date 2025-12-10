import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

export interface HotwordRecord {
  id: number;
  word: string;
  status: number;
  create_time: string;
  update_time: string;
}

export const columns: TableColumnData[] = [
  {
    title: 'ID',
    dataIndex: 'id',
    width: 80
  },
  {
    title: '热词',
    dataIndex: 'word',
    minWidth: 200
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    width: 100,
    align: 'center'
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    width: 180
  },
  {
    title: '操作',
    slotName: 'operations',
    width: 180,
    fixed: 'right',
    align: 'center'
  }
];
