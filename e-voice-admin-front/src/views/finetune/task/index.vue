<template>
  <div class="container">
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16">
          <ASpace>
            <AInput v-model="formModel.title" :style="{ width: '160px' }" placeholder="名称" allow-clear />
            <ARangePicker v-model="formModel.createdTime" :style="{ width: '200px' }" />
            <ASelect
              v-model="formModel.status"
              :options="statusOptions"
              placeholder="状态"
              :style="{ width: '120px' }"
            />
            <AButton type="primary" :loading="btnLoading" @click="search">
              <template #icon>
                <icon-search />
              </template>
              查询
            </AButton>
            <AButton @click="reset">重置</AButton>
          </ASpace>
        </ACol>
        <ACol :span="8" style="text-align: right">
          <ASpace>
            <AButton type="primary" @click="handleCreate">
              <template #icon>
                <icon-plus />
              </template>
              新建
            </AButton>
            <ATooltip content="刷新">
              <div class="action-icon" @click="search"><icon-refresh size="18" /></div>
            </ATooltip>
          </ASpace>
        </ACol>
      </ARow>
      <ATable
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="columns"
        :data="renderData"
        :bordered="{ wrapper: true, cell: true }"
        :size="size"
        :default-expand-all-rows="true"
        @page-change="handlePaageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #name="{ record }">
          {{ record.name }}
          <span v-if="record.nickname" style="padding-left: 5px; color: var(--color-neutral-4)">
            {{ record.nickname }}
          </span>
        </template>
        <template #image="{ record }">
          <img alt="" style="height: 50px; border-radius: 5px" :src="record.image" />
        </template>
        <template #status="{ record }">
          <ATag v-if="record.status === 1" color="rgb(var(--danger-6))" size="small">训练中</ATag>
          <ATag v-else-if="record.status === 2" color="rgb(var(--success-6))" size="small">训练完成</ATag>
          <ATag v-else-if="record.status === 3" color="rgb(var(--primary-6))" size="small">待训练</ATag>
        </template>
        <template #operations="{ record }">
          <ASpace class="option">
            <APopconfirm content="您确定开始训练吗?" @ok="handleTrain(record)">
              <ATooltip content="开始微调">
                <Icon v-if="record.status === 3" icon="icon-robot" color="rgb(var(--success-6))" />
              </ATooltip>
            </APopconfirm>
            <Icon icon="icon-edit" color="rgb(var(--primary-6))" @click="handleEdit(record)" />
            <ATooltip content="日志">
              <Icon icon="icon-file" color="rgb(var(--primary-6))" @click="handleLog(record)" />
            </ATooltip>
            <ATooltip v-if="record.status === 2" content="测试模型">
              <Icon icon="icon-safe" color="rgb(var(--warning-6))" @click="handleTest(record)" />
            </ATooltip>
            <ATooltip v-if="record.status === 2" content="应用">
              <Icon icon="icon-check" color="rgb(var(--success-6))" @click="handleAdopt(record)" />
            </ATooltip>
            <APopconfirm content="您确定要删除吗?" @ok="handleDel(record)">
              <ATooltip content="删除">
                <Icon icon="icon-delete" :size="18" color="#ed6f6f" />
              </ATooltip>
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!--表单-->
    <AddForm @register="registerModal" @success="handleData" />
  </div>
  <Log :log-model="logModel" @success="handleTaskSuccess" />
</template>

<script lang="ts" setup>
import { useRoute } from 'vue-router';
import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import type { Pagination } from '@/types/global';
import { useModal } from '@/components/Modal';
import type { LogModel } from '@/views/finetune/task/Log.vue';
import Log from '@/views/finetune/task/Log.vue';
import AddForm from './AddForm.vue';
import { columns } from './data';
import { del, getList, save, start } from './api';

const route = useRoute();
const [registerModal, { openModal }] = useModal();

// 分页
const basePagination: Pagination = {
  current: 1,
  pageSize: 10
};
const pagination = reactive({
  ...basePagination,
  showTotal: true,
  showPageSize: true
});
type SizeProps = 'mini' | 'small' | 'medium' | 'large';
const { loading, setLoading } = useLoading(true);
const { loading: btnLoading, setLoading: setBtnLoading } = useLoading(false);
const renderData = ref([]);
const size = ref<SizeProps>('large');
// 查询字段
const generateFormModel = () => {
  return {
    trade_no: '',
    title: '',
    name: '',
    createdTime: [],
    status: ''
  };
};
const formModel = ref(generateFormModel());
const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getList({ page: pagination.current, pageSize: pagination.pageSize, ...formModel.value });
    renderData.value = data.items;
    pagination.current = data.page;
    pagination.total = data.total;
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};
// 查找
const search = () => {
  setBtnLoading(true);
  fetchData();
  setTimeout(() => {
    setBtnLoading(false);
  }, 1000);
};
const reset = () => {
  formModel.value = generateFormModel();
  fetchData();
};

fetchData();

// 添加
const handleCreate = () => {
  openModal(true, {
    isUpdate: false,
    record: null
  });
};
// 编辑数据
const handleEdit = async (record: any) => {
  openModal(true, {
    isUpdate: true,
    record
  });
};

const logModel = ref<LogModel>({
  taskId: 0,
  visible: false,
  running: false
});

const current = ref();

const handleLog = async (record: any) => {
  logModel.value = {
    visible: true,
    taskId: record.id,
    running: record.status === 1
  };
  current.value = record;
};

const handleAdopt = async (record: any) => {
  console.log(record);
};

const handleTest = async (record: any) => {
  console.log(record);
};

const handleTrain = async (record: any) => {
  console.log(record);
  await start({ id: record.id });
  record.status = 1;
  await handleLog(record);
  Message.success({ content: '开始训练成功' });
};
// 更新数据
const handleData = async () => {
  await fetchData();
};
// 分页
const handlePaageChange = (page: any) => {
  pagination.current = page;
  fetchData();
};
// 分页总数
const handlePageSizeChange = (pageSize: any) => {
  pagination.pageSize = pageSize;
  fetchData();
};
// 删除数据
const handleDel = async (record: any) => {
  Message.loading({ content: '删除中', id: 'upStatus' });
  const res = await del({ ids: [record.id] });
  if (res) {
    await fetchData();
    Message.success({ content: '删除成功', id: 'upStatus' });
  }
};

const handleTaskSuccess = async () => {
  if (current.value.status !== 2) {
    current.value.status = 2;
    await save({ id: current.value.id, status: 2 });
  }
};
// 状态
const statusOptions = computed<SelectOptionData[]>(() => [
  {
    label: '全部',
    value: ''
  },
  {
    label: '正常',
    value: 0
  },
  {
    label: '隐藏',
    value: 1
  }
]);
</script>

<style scoped lang="less">
:deep(.arco-table-th) {
  &:last-child {
    .arco-table-th-item-title {
      margin-left: 16px;
    }
  }
}
.action-icon {
  margin-left: 12px;
  cursor: pointer;
}
.active {
  color: #0960bd;
  background-color: #e3f4fc;
}
.setting {
  display: flex;
  align-items: center;
  width: 200px;
  .title {
    margin-left: 12px;
    cursor: pointer;
  }
}
:deep(.general-card > .arco-card-header) {
  padding: 10px 16px;
}
.option .arco-icon {
  user-select: none;
  cursor: pointer;
  opacity: 0.8;
  &:hover {
    opacity: 1;
  }
}
</style>
