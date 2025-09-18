import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = computed<TableColumnData[]>(() => [
  {
    title: '菜单名称',
    dataIndex: 'title',
    slotName: 'title'
  },
  {
    title: '图标',
    dataIndex: 'icon',
    slotName: 'icon',
    align: 'center'
  },
  {
    title: '类型',
    dataIndex: 'type',
    slotName: 'type',
    align: 'center'
  },
  {
    title: '组件/权限',
    dataIndex: 'component',
    slotName: 'component'
  },
  {
    title: '排序',
    dataIndex: 'orderNo',
    slotName: 'orderNo',
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
    title: '操作',
    dataIndex: 'operations',
    slotName: 'operations',
    align: 'center'
  }
]);
