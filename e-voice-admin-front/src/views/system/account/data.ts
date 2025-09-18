import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = computed<TableColumnData[]>(() => [
  {
    title: '用户名',
    dataIndex: 'name',
    slotName: 'name'
  },
  {
    title: '头像',
    dataIndex: 'avatar',
    slotName: 'avatar',
    align: 'center'
  },
  {
    title: '角色',
    dataIndex: 'rolename'
  },
  {
    title: '部门',
    dataIndex: 'depname'
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    slotName: 'email'
  },
  {
    title: '备注',
    dataIndex: 'remark',
    slotName: 'remark',
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
