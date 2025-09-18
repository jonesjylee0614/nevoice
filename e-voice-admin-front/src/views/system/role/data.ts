import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = computed<TableColumnData[]>(() => [
  {
    title: '角色名称',
    dataIndex: 'name',
    slotName: 'title'
  },
  {
    title: 'ID',
    dataIndex: 'id',
    align: 'center'
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    align: 'center'
  },
  {
    title: '修改人',
    dataIndex: 'updaterName',
    slotName: 'updaterName',
    align: 'center'
  },
  {
    title: '修改时间',
    dataIndex: 'updateTime',
    slotName: 'updateTime',
    align: 'center'
  },
  {
    title: '备注',
    dataIndex: 'remark'
  },
  {
    title: '操作',
    dataIndex: 'operations',
    slotName: 'operations',
    align: 'center'
  }
]);
export interface TreeItem {
  id?: number;
  pid?: number;
  title?: string;
}
