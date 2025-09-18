<template>
  <div class="container">
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <ACard ref="oneLineCardRef" class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16">
          <ASpace>
            <AInput v-model="formModel.name" :style="{ width: '160px' }" placeholder="用户名" allow-clear />
            <AButton type="primary" @click="search">
              <template #icon>
                <icon-search />
              </template>
              查询
            </AButton>
            <AButton @click="reset">重置</AButton>
            <AButton disabled>范文管理</AButton>
            <AButton status="warning" @click="openIdentityForm">声纹鉴定</AButton>
            <AButton status="success" @click="openRealtimeForm">实时语音识别</AButton>
          </ASpace>
        </ACol>
        <ACol :span="8" style="text-align: right">
          <ASpace>
            <AButton type="primary" @click="createRule">
              <template #icon>
                <icon-info-circle />
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
        ref="artable"
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="cloneColumns as TableColumnData[]"
        :data="renderData"
        :bordered="{ wrapper: true, cell: true }"
        :size="size"
        :default-expand-all-rows="true"
        @page-change="handlePageChange"
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
        <template #avatar="{ record }">
          <AImage alt="" width="30px" style="cursor: pointer; border-radius: 5px" :src="record.avatar" />
        </template>
        <template #options="{ record }">
          <ASpace class="option">
            <ATooltip content="声纹管理">
              <Icon icon="icon-message" color="rgb(var(--primary-6))" @click="handlePrints(record)" />
            </ATooltip>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!--表单-->
    <!--    <AddForm @register="registerModal" @success="handleData" />-->
    <PrintsForm @register="registerModal" @success="handleData" />
    <IdentifyForm @register="registerIdentityModal" />
    <RealtimeForm @register="registerRealtimeModal" />
  </div>
</template>

<script lang="ts" setup>
import { useRoute } from 'vue-router';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
import cloneDeep from 'lodash/cloneDeep';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { useModal } from '@/components/Modal';
import { Icon } from '@/components/Icon';
import type { Pagination } from '/#/global';
import IdentifyForm from '@/views/voice/print/IdentifyForm.vue';
import RealtimeForm from '@/views/voice/print/RealtimeForm.vue';
import { getUserList } from './api';
import { columns } from './data';
import PrintsForm from './PrintsForm.vue';
defineOptions({
  name: 'Print'
});

// 按钮权限写到一起
const perms = {
  add: 'print:add',
  del: 'print:del',
  edit: 'print:edit'
};

const route = useRoute();
const [registerModal, { openModal }] = useModal();
const [registerIdentityModal, { openModal: openIdentityForm }] = useModal();
const [registerRealtimeModal, { openModal: openRealtimeForm }] = useModal();
const oneLineCardRef = ref(null);
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
type Column = TableColumnData & { checked?: true };
const { loading, setLoading } = useLoading(true);
const renderData = ref([]);
const cloneColumns = ref<Column[]>([]);
const showColumns = ref<Column[]>([]);
const size = ref<SizeProps>('large');
// 查询字段
const generateFormModel = () => {
  return {
    name: ''
  };
};
const formModel = ref(generateFormModel());
const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getUserList({ page: pagination.current, pageSize: pagination.pageSize, ...formModel.value });
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
  fetchData();
};
const reset = () => {
  formModel.value = generateFormModel();
  fetchData();
};

fetchData();

watch(
  () => columns.value,
  val => {
    cloneColumns.value = cloneDeep(val);
    cloneColumns.value.forEach((item, index) => {
      item.checked = true;
    });
    showColumns.value = cloneDeep(cloneColumns.value);
  },
  { deep: true, immediate: true }
);
// 添加
const createRule = () => {
  Message.warning('请在【系统设置-账户管理】中添加带有【声纹注册用户】角色的用户');
};
// 编辑数据
const handlePrints = async (record: any) => {
  openModal(true, {
    isUpdate: true,
    record
  });
};
// 更新数据
const handleData = async () => {
  fetchData();
};
// 分页
const handlePageChange = (page: any) => {
  pagination.current = page;
  fetchData();
};
// 分页总数
const handlePageSizeChange = (pageSize: any) => {
  pagination.pageSize = pageSize;
  fetchData();
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
</style>
