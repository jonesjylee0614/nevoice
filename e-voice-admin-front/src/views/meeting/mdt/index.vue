<template>
  <div class="container">
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16">
          <ASpace>
            <AInput v-model="formModel.title" :style="{ width: '160px' }" placeholder="会议标题" allow-clear />
            <AInput v-model="formModel.hostName" :style="{ width: '120px' }" placeholder="主持人" allow-clear />
            <ASelect v-model="formModel.status" :style="{ width: '100px' }" placeholder="状态" allow-clear>
              <AOption :value="0">待开始</AOption>
              <AOption :value="1">进行中</AOption>
              <AOption :value="2">已结束</AOption>
            </ASelect>
            <ARangePicker v-model="formModel.createdTime" :style="{ width: '230px' }" />
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
            <AButton v-perm="[perms.edit]" type="primary" @click="handleCreate">
              <template #icon>
                <icon-plus />
              </template>
              新建会议
            </AButton>
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
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #status="{ record }">
          <ATag :color="meetingStatusMap[record.status]?.color || 'gray'">
            {{ meetingStatusMap[record.status]?.text || '未知' }}
          </ATag>
        </template>
        <template #summaryStatus="{ record }">
          <ATag :color="summaryStatusMap[record.summaryStatus]?.color || 'gray'">
            {{ summaryStatusMap[record.summaryStatus]?.text || '未知' }}
          </ATag>
        </template>
        <template #operations="{ record }">
          <ASpace class="option">
            <ATooltip v-perm="[perms.detail]" content="详情">
              <Icon icon="icon-list" color="rgb(var(--primary-6))" @click="handleDetail(record)" />
            </ATooltip>
            <ATooltip v-perm="[perms.edit]" content="编辑">
              <Icon icon="icon-edit" color="rgb(var(--primary-6))" @click="handleEdit(record)" />
            </ATooltip>
            <APopconfirm v-perm="[perms.del]" content="确定要删除吗?" @ok="handleDel(record)">
              <ATooltip content="删除">
                <Icon icon="icon-delete" :size="18" color="#ed6f6f" />
              </ATooltip>
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!-- 新建/编辑表单 -->
    <AddForm @register="registerModal" @success="handleData" />
  </div>
</template>

<script lang="ts" setup>
import { useRoute, useRouter } from 'vue-router';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import type { Pagination } from '@/types/global';
import { useModal } from '@/components/Modal';
import { columns, meetingStatusMap, summaryStatusMap } from './data';
import AddForm from './AddForm.vue';
import { del, getList } from './api';

const route = useRoute();
const router = useRouter();
const [registerModal, { openModal }] = useModal();

// 按钮权限
const perms = {
  del: 'meeting:mdt:del',
  edit: 'meeting:mdt:edit',
  detail: 'meeting:mdt:detail'
};

// 分页配置
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

// 查询条件
const generateFormModel = () => {
  return {
    title: '',
    hostName: '',
    status: undefined as number | undefined,
    createdTime: []
  };
};
const formModel = ref(generateFormModel());

// 获取列表数据
const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getList({
      page: pagination.current,
      pageSize: pagination.pageSize,
      ...formModel.value
    });
    renderData.value = data.items;
    pagination.current = data.page;
    pagination.total = data.total;
  } catch (err) {
    // 错误处理
  } finally {
    setLoading(false);
  }
};

// 查询
const search = () => {
  setBtnLoading(true);
  pagination.current = 1;
  fetchData();
  setTimeout(() => {
    setBtnLoading(false);
  }, 1000);
};

// 重置
const reset = () => {
  formModel.value = generateFormModel();
  pagination.current = 1;
  fetchData();
};

// 初始化加载
fetchData();

// 新建会议
const handleCreate = () => {
  openModal(true, {
    isUpdate: false,
    record: null
  });
};

// 编辑会议
const handleEdit = (record: any) => {
  openModal(true, {
    isUpdate: true,
    record
  });
};

// 查看详情
const handleDetail = (record: any) => {
  router.push({
    path: '/meeting/mdt/detail',
    query: { id: record.id }
  });
};

// 更新数据
const handleData = () => {
  setTimeout(fetchData, 1000);
};

// 分页
const handlePageChange = (page: number) => {
  pagination.current = page;
  fetchData();
};

// 每页条数
const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize;
  fetchData();
};

// 删除
const handleDel = async (record: any) => {
  try {
    Message.loading({ content: '删除中', id: 'upStatus' });
    const res = await del({ ids: [record.id] });
    if (res) {
      fetchData();
      Message.success({ content: '删除成功', id: 'upStatus' });
    }
  } catch (error) {
    Message.clear('top');
  }
};
</script>

<style scoped lang="less">
:deep(.arco-table-th) {
  &:last-child {
    .arco-table-th-item-title {
      margin-left: 16px;
    }
  }
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
