<template>
  <div class="container">
    <Breadcrumb :items="['menu.system', 'menu.system.rule']" />
    <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16"></ACol>
        <ACol :span="8" style="text-align: right">
          <ASpace>
            <AButton type="primary" @click="handleExpand">
              {{ expanded ? '收起' : '展开' }}
            </AButton>
            <AButton v-perm="[perms.edit]" type="primary" @click="handleCreate">
              <template #icon>
                <icon-plus />
              </template>
              {{ $t('searchTable.operation.create') }}
            </AButton>
            <ATooltip :content="$t('searchTable.actions.refresh')">
              <div class="action-icon" @click="search">
                <icon-refresh size="18" />
              </div>
            </ATooltip>
          </ASpace>
        </ACol>
      </ARow>
      <ATable
        ref="artable"
        row-key="id"
        :loading="loading"
        :pagination="false"
        :columns="cloneColumns as TableColumnData[]"
        :data="renderData"
        :bordered="{ wrapper: true, cell: true }"
        :size="size"
        :default-expand-all-rows="true"
        @change="handleChange"
      >
        <template #title="{ record }">
          <!--          <span style="padding-right: 5px; color: var(&#45;&#45;color-neutral-4)" v-html="record.spacer"></span>-->
          {{ record.title }}
        </template>
        <template #icon="{ record }">
          <Icon :icon="record.icon" :size="20" />
        </template>
        <template #createTime="{ record }">
          {{ dayjs(record.createTime).format('YYYY-MM-DD') }}
        </template>
        <template #orderNo="{ record }">
          <AInput
            v-model.number="record.orderNo"
            style="width: 50px"
            size="mini"
            :min="0"
            @change="handleOrderNum(record)"
          />
        </template>
        <template #component="{ record }">
          <ATag v-if="record.type === 2" color="green" default-checked>{{ record.permission }}</ATag>
          <ATag v-else-if="record.type === 1" color="arcoblue" default-checked>{{ record.component }}</ATag>
          <ATag v-else color="cyan" default-checked>{{ record.component }}</ATag>
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
        <template #type="{ record }">
          <ATag v-if="record.type === 2" color="green" default-checked>按钮</ATag>
          <ATag v-else-if="record.type === 1" color="arcoblue" default-checked>菜单</ATag>
          <ATag v-else color="cyan" default-checked>目录</ATag>
        </template>
        <template #operations="{ record }">
          <ASpace class="option">
            <ATooltip v-if="record.type < 2" v-perm="[perms.edit]" position="top" trigger="hover" content="添加菜单">
              <Icon icon="icon-plus" :size="18" color="rgb(var(--primary-6))" @click="handleAddMenu(record)" />
            </ATooltip>
            <ATooltip v-if="record.type < 2" v-perm="[perms.edit]" position="top" trigger="hover" content="添加权限">
              <Icon icon="icon-plus" :size="18" color="rgb(var(--green-6))" @click="handleAddPerm(record)" />
            </ATooltip>
            <ATooltip v-perm="[perms.edit]" position="top" trigger="hover" content="修改">
              <Icon icon="icon-edit" :size="18" color="rgb(var(--primary-6))" @click="handleEdit(record)" />
            </ATooltip>
            <ATooltip v-perm="[perms.del]" position="top" trigger="hover" content="删除">
              <APopconfirm content="您确定要删除吗?" @ok="handleDel(record)">
                <Icon icon="icon-delete" :size="18" color="#ed6f6f" />
              </APopconfirm>
            </ATooltip>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!--表单-->
    <AddForm @register="registerModal" @success="handleData" />
  </div>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import cloneDeep from 'lodash/cloneDeep';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
import { Message } from '@arco-design/web-vue';
import { del, getList, upOrder, upStatus } from '@/api/system/rule';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import { useModal } from '@/components/Modal';
import AddForm from './AddForm.vue';
import { columns } from './data';
defineOptions({
  name: 'Rule'
});
const perms = {
  edit: 'rule:edit',
  del: 'rule:del',
  upStatus: 'rule:upStatus'
};
const [registerModal, { openModal }] = useModal();
type SizeProps = 'mini' | 'small' | 'medium' | 'large';
type Column = TableColumnData & { checked?: true };
const { loading, setLoading } = useLoading(true);
const renderData = ref([]);
const expanded = ref(false);
const cloneColumns = ref<Column[]>([]);
const showColumns = ref<Column[]>([]);
const size = ref<SizeProps>('large');
const artable = ref();
const fetchData = async () => {
  setLoading(true);
  try {
    renderData.value = await getList({});
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};

const search = () => {
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
// 添加菜单
const handleCreate = () => {
  openModal(true, {
    isUpdate: false,
    record: null
  });
};
const handleExpand = () => {
  expanded.value = !expanded.value;
  artable.value.expandAll(expanded.value);
};
// 添加菜单
const handleAddMenu = (record: any) => {
  openModal(true, {
    isUpdate: false,
    record: { type: 1, pid: record.id }
  });
};
// 添加菜单
const handleAddPerm = (record: any) => {
  openModal(true, {
    isUpdate: false,
    record: { type: 2, pid: record.id }
  });
};
// 编辑数据
const handleEdit = async (record: any) => {
  openModal(true, {
    isUpdate: true,
    record
  });
};
// 更新数据
const handleData = async () => {
  fetchData();
};
// 排序拖拽
const handleChange = (_data: any) => {
  renderData.value = _data;
};
// 更新状态
const handleStatus = async (record: any) => {
  const res = await upStatus({ id: record.id, status: record.status });
  if (res) {
    Message.success({ content: '更新状态成功', id: 'upStatus' });
  }
};
const handleOrderNum = async (record: any) => {
  const res = await upOrder({ id: record.id, orderNo: record.orderNo });
  if (res) {
    Message.success({ content: '更新状态成功', id: 'upStatus' });
  }
};
// 删除数据
const handleDel = async (record: any) => {
  const res = await del({ ids: [record.id] });
  if (res) {
    fetchData();
    Message.success({ content: '删除成功', id: 'upStatus' });
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
