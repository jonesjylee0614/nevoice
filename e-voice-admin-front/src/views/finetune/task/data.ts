import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = [
  {
    title: '微调任务名',
    dataIndex: 'name',
    align: 'left'
  },
  {
    title: '模型产物路径',
    dataIndex: 'modelPath',
    slotName: 'modelPath',
    align: 'left'
  },
  {
    title: '运行状态',
    dataIndex: 'status',
    slotName: 'status',
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
