<template>
  <div class="container">
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <div class="flexbox">
        <div class="menu">
          <div class="btn">
            <ASpace>
              <AButton v-perm="[perms.edit]" type="primary" @click="AddMenuData(1)">
                <icon-plus />
                <span style="padding-left: 3px">添加</span>
              </AButton>
              <AButton v-perm="[perms.edit]" type="primary" status="warning" @click="AddMenuData(2)">
                <icon-edit />
                <span style="padding-left: 3px">修改</span>
              </AButton>
              <AButton v-perm="[perms.del]" type="primary" status="danger" @click="delMenuData">
                <icon-delete />
                <span style="padding-left: 3px">删除</span>
              </AButton>
            </ASpace>
          </div>
          <div class="tablebox">
            <ATable
              :data="menuData"
              row-key="id"
              :selected-keys="selectedKeys"
              :scrollbar="true"
              :pagination="false"
              :bordered="{ wrapper: true, cell: true }"
              style="margin-top: 10px"
              @row-click="handleClickMenu"
            >
              <template #columns>
                <!-- <ATableColumn title="" :width="50" data-index="id"></ATableColumn> -->
                <ATableColumn title="字典名称" data-index="title">
                  <template #cell="{ record }">
                    <div class="titlebox">
                      <div class="text">{{ record.title }}</div>
                      <div class="icon"><icon-right /></div>
                    </div>
                  </template>
                </ATableColumn>
              </template>
            </ATable>
          </div>
        </div>
        <div class="content">
          <ARow style="margin-bottom: 10px; padding: 0 10px">
            <ACol :span="16">
              <ASpace>
                <AInput
                  v-model="formModel.title"
                  :style="{ width: '160px' }"
                  placeholder="字典项名"
                  allow-clear
                  @keyup.enter="search"
                />
                <AButton type="primary" @click="search">
                  <template #icon>
                    <icon-search />
                  </template>
                  查询
                </AButton>
                <AButton @click="reset">
                  {{ $t('searchTable.form.reset') }}
                </AButton>
              </ASpace>
            </ACol>
            <ACol :span="8" style="text-align: right">
              <ASpace>
                <AButton v-perm="[perms.edit]" type="primary" @click="handleCreate">
                  <template #icon>
                    <icon-plus />
                  </template>
                  {{ $t('searchTable.operation.create') }}
                </AButton>
                <ATooltip :content="$t('searchTable.actions.refresh')">
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
              <img alt="封面" style="height: 50px; border-radius: 5px" :src="record.image" />
            </template>
            <template #updateTime="{ record }">
              {{ dayjs(record.updateTime).format('YYYY-MM-DD') }}
            </template>
            <template #status="{ record }">
              <ASwitch
                v-model="record.status"
                v-perm="[perms.upStatus]"
                type="round"
                :checked-value="0"
                :unchecked-value="1"
                @change="handleStatus(record)"
              >
                <template #checked>开</template>
                <template #unchecked>关</template>
              </ASwitch>
            </template>
            <template #operations="{ record }">
              <ASpace class="option">
                <Icon
                  v-perm="[perms.edit]"
                  icon="icon-edit"
                  color="rgb(var(--primary-6))"
                  @click="handleEdit(record)"
                />
                <APopconfirm v-perm="[perms.del]" content="您确定要删除吗?" @ok="handleDel(record)">
                  <Icon icon="icon-delete" :size="18" color="#ed6f6f" />
                </APopconfirm>
              </ASpace>
            </template>
          </ATable>
        </div>
      </div>
    </ACard>
    <!--表单-->
    <AddForm @register="registerModal" @success="handleData" />
    <AddMenu @register="registerAddMenuModal" @success="handleAddMenu" />
  </div>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
import cloneDeep from 'lodash/cloneDeep';
import { Message, Modal } from '@arco-design/web-vue';
import { delMenuList, getmenuList } from '@/api/datacenter/tabledata';
import type { menuItem } from '@/api/datacenter/tabledata';
import { del, getList, upStatus } from '@/api/datacenter/dictionary';
import { useUserStore } from '@/store';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import type { Pagination } from '@/types/global';
import { useModal } from '@/components/Modal';
import AddMenu from './AddMenu.vue';
import AddForm from './AddForm.vue';
import { columns } from './data';
defineOptions({
  name: 'Dictionary'
});
const perms = {
  edit: 'dict:edit',
  del: 'dict:del',
  upStatus: 'dict:upStatus'
};

const userInfo = useUserStore();
const route = useRoute();
const [registerModal, { openModal }] = useModal();
const [registerAddMenuModal, { openModal: openAddMenuModal }] = useModal();

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
const menuData = ref<menuItem[]>([]);
const cloneColumns = ref<Column[]>([]);
const showColumns = ref<Column[]>([]);
const size = ref<SizeProps>('large');
// 查询字段
const generateFormModel = () => {
  return {
    trade_no: '',
    title: '',
    name: '',
    status: ''
  };
};
const formModel = ref(generateFormModel());
const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getList({
      page: pagination.current,
      pageSize: pagination.pageSize,
      dicId: menuitem.value!.id,
      ...formModel.value
    });
    renderData.value = data.items;
    pagination.current = data.page;
    pagination.total = data.total;
  } finally {
    setLoading(false);
  }
};
// 获取左边数据
const menuitem = ref<menuItem>();
const getmenudata = async () => {
  menuData.value = await getmenuList({});
  if (menuData.value && menuData.value.length > 0) {
    selectedKeys.value = [menuData.value[0].id];
    menuitem.value = menuData.value[0];
    await nextTick(() => {
      fetchData();
    });
  }
};
// 更新左边数据
const handleAddMenu = () => {
  getmenudata();
};
// 选择菜单数据
const selectedKeys = ref<number[]>([]);
const handleClickMenu = (row: any) => {
  renderData.value = [];
  pagination.current = 1;
  setLoading(true);
  selectedKeys.value = [row.id];
  menuitem.value = row;
  fetchData();
};
// 添加菜单数据
const AddMenuData = (type: number) => {
  console.log(menuitem.value?.data_from);
  if (type == 2 && !menuitem.value) {
    Message.error('未选择编辑数据');
  } else if (
    type == 2 &&
    menuitem.value?.data_from == 'common' &&
    menuitem.value?.businessID != userInfo.$state.userId
  ) {
    Message.error('您没有编辑权限，只能编辑自己添加数据');
  } else {
    openAddMenuModal(true, {
      isUpdate: type == 2,
      record: type == 2 ? menuitem : null
    });
  }
};
// 删除菜单数据
const delMenuData = () => {
  if (!selectedKeys.value || selectedKeys.value.length == 0) {
    Message.error('未选择删除数据');
  } else if (menuitem.value?.data_from == 'common' || menuitem.value?.businessID != userInfo.$state.userId) {
    Message.error('数据不可编辑');
  } else {
    Modal.warning({
      title: '您确定要删除内容吗？',
      content: '删除后内容将无法恢复请谨慎操作！',
      cancelText: '取消',
      okText: '删除',
      titleAlign: 'start',
      hideCancel: false,
      onOk: async () => {
        await delMenuList({ ids: selectedKeys.value });
        nextTick(() => {
          Message.success({
            content: '删除成功',
            id: 'upStatus',
            duration: 200
          });
          getmenudata();
        });
      }
    });
  }
};
// 组件挂载完成后执行的函数
onMounted(() => {
  getmenudata();
});
// 查找
const search = () => {
  fetchData();
};
const reset = () => {
  formModel.value = generateFormModel();
  fetchData();
};

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
const handleCreate = () => {
  if (!selectedKeys.value || selectedKeys.value.length == 0) {
    Message.error('未选择字典数据');
  } else {
    openModal(true, {
      isUpdate: false,
      table_id: selectedKeys.value[0],
      record: null
    });
  }
};
// 编辑数据
const handleEdit = async (record: any) => {
  openModal(true, {
    isUpdate: true,
    table_id: selectedKeys.value[0],
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
// 更新状态
const handleStatus = async (record: any) => {
  try {
    const res = await upStatus({
      id: record.id,
      status: record.status
    });
    if (res) {
      Message.success({ content: '更新状态成功', id: 'upStatus' });
    }
  } catch (error) {}
};
// 删除数据
const handleDel = async (record: any) => {
  try {
    const res = await del({
      ids: [record.id]
    });
    if (res) {
      fetchData();
      Message.success({ content: '删除成功', id: 'upStatus' });
    }
  } catch (error) {}
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
.container {
  padding: 0 20px 20px 20px;
  height: 100%;
  .flexbox {
    display: flex;
    justify-content: space-between; // 替代原先的space-between布局方式
    height: 100%;
    .menu {
      width: 230px;
      margin-right: 10px;
      background-color: var(--color-neutral-1);
      padding: 10px 0;
      .btn {
        text-align: center;
      }
      .tablebox {
        //分类标题背景色
        :deep(.arco-table-th) {
          background-color: var(--color-neutral-3);
        }
        :deep(.arco-table-tr-checked .arco-table-td) {
          color: rgb(var(--primary-6));
        }
        .titlebox {
          display: flex;
          .text {
            flex: 1;
          }
        }
      }
    }
    .content {
      flex: 1;
      min-width: 400px;
      background-color: var(--color-neutral-1);
      padding: 10px 0;
      min-height: 650px;
    }
  }
}
:deep(.arco-btn-size-medium) {
  padding: 0 10px;
}
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
