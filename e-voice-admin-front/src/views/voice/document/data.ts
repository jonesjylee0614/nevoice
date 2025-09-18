import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

export interface DocumentRecord {
  id: number;
  name: string;
  content: string;
  status: number;
  create_time: string;
  update_time: string;
}

export const columns: TableColumnData[] = [
  {
    title: 'ID',
    dataIndex: 'id',
    width: 80,
  },
  {
    title: '标题',
    dataIndex: 'name',
    minWidth: 150,
  },
  {
    title: '状态',
    dataIndex: 'status',
    width: 100,
    align: 'center',
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    width: 180,
  },
  {
    title: '更新时间',
    dataIndex: 'update_time',
    width: 180,
  },
];