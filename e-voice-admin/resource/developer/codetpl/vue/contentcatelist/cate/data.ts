import type {TableColumnData} from '@arco-design/web-vue/es/table/interface';

export const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width:80,
      align:"center"
    },
    {
      title: '名称',
      dataIndex: 'name',
      align:"center"
    },
    {
      title: '描述',
      dataIndex: 'des',
      align:"center"
    },
    {
      title: '状态',
      dataIndex: 'status',
      slotName: 'status',
      align:"center"
    },
    {
      title: '创建时间',
      dataIndex: 'createTime',
      slotName: 'createTime',
      align:"center"
    },
    {
      title: '操作',
      dataIndex: 'operations',
      slotName: 'operations',
      align:"center"
    },
  ] as TableColumnData[];