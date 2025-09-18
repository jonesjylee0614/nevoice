import { computed } from 'vue';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
export const columns = computed<TableColumnData[]>(() => [
  {
    title: '用户ID',
    dataIndex: 'id',
    align: 'center',
    width: 100
  },
  {
    title: '用户名',
    dataIndex: 'username',
    align: 'left'
  },
  {
    title: '姓名',
    dataIndex: 'name',
    slotName: 'name',
    align: 'left'
  },
  {
    title: '头像',
    dataIndex: 'avatar',
    slotName: 'avatar',
    align: 'center',
    width: 100
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
