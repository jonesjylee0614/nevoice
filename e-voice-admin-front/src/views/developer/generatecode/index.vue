<template>
  <div class="container">
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <ACard ref="oneLineCardRef" class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16">
          <ASpace>
            <AInput
              v-model="formModel.name"
              :style="{ width: '120px' }"
              placeholder="标题"
              allow-clear
              @keyup.enter="search"
            />
            <ARangePicker v-model="formModel.createdTime" :style="{ width: '200px' }" />
            <ASelect
              v-model="formModel.status"
              :options="statusOptions"
              placeholder="状态"
              :style="{ width: '120px' }"
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
            <AButton type="primary" @click="addTable">
              <template #icon>
                <icon-plus />
              </template>
              添加表
            </AButton>
            <AButton type="primary" @click="updateTable">
              <template #icon>
                <icon-refresh />
              </template>
              更新数据表
            </AButton>
            <ATooltip :content="$t('searchTable.actions.refresh')">
              <div class="action-icon" @click="search"><icon-refresh size="18" /></div>
            </ATooltip>
          </ASpace>
        </ACol>
      </ARow>
      <div class="tablebox">
        <ATable
          row-key="id"
          :loading="loading"
          :pagination="pagination"
          :columns="cloneColumns"
          :data="renderData"
          :bordered="{ wrapper: true, cell: true }"
          :size="size"
          :default-expand-all-rows="true"
          :scroll="{ x: cardboxWidth }"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        >
          <template #image="{ record }">
            <img alt="封面" style="height: 50px; border-radius: 5px" :src="record.image" />
          </template>
          <template #createTime="{ record, column }">
            {{ dayjs(record[column.dataIndex]).format('YYYY-MM-DD HH:MM:SS') }}
          </template>
          <template #overtime="{ record }">
            {{ record.overtime == 0 ? '不限' : record.overtime }}
          </template>
          <template #status="{ record }">
            <ASwitch
              v-model="record.status"
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
              <AButton style="color: rgb(var(--arcoblue-6))" @click="openCodeMaker(record)">生成</AButton>
              <APopconfirm
                :content="`您确定要${record.is_install == 1 ? '卸载' : '删除'}数据库和代码吗?`"
                @ok="handleDel(record)"
              >
                <AButton status="danger">{{ record.is_install == 1 ? '卸载' : '删除' }}</AButton>
              </APopconfirm>
            </ASpace>
          </template>
        </ATable>
      </div>
      <div class="tigbox">
        <div class="title">生成代码说明：</div>
        <div class="item">
          <div class="label">1.新增数据表时，请点击右上角的“更新数据表”进行更新</div>
        </div>
        <div class="item">
          <div class="label">2.生成数据列表不带分类，则直接选择“模板类型=仅数据列表”</div>
          <div class="text"></div>
        </div>
        <div class="item">
          <div class="label">
            3.生成列表数据时，如果数据有对应分类（如：产品分类）时“模板类型=数据关联分类”，产品列表数据表命名为：business_product_content
            分类数据表命名为：business_product__cate
          </div>
          <div class="text"></div>
        </div>
        <div class="item">
          <div class="label">
            4.生成更多配置说明请到
            <a
              href="https://doc.goflys.cn/docview?id=25&fid=275"
              target="_blank"
              rel="noopener noreferrer"
              style="color: #165dff"
            >
              开发文档查看
            </a>
          </div>
          <div class="text"></div>
        </div>
      </div>
    </ACard>
  </div>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
import cloneDeep from 'lodash/cloneDeep';
import { Message } from '@arco-design/web-vue';
import { del, getList, upCodeTable, upStatus } from '@/api/developer/generatecode';
import useLoading from '@/hooks/loading';
import type { Pagination } from '@/types/global';
import { columns } from './data';
defineOptions({
  name: 'Rule'
});

const route = useRoute();
const router = useRouter();
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
    trade_no: '',
    name: '',
    createdTime: [],
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
      ...formModel.value
    });
    renderData.value = data.items;
    pagination.current = data.page;
    pagination.total = data.total;
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};
// 查询
const search = () => {
  fetchData();
};
const reset = () => {
  formModel.value = generateFormModel();
  fetchData();
};
// 组件挂载完成后执行的函数
const timer = ref();
onMounted(() => {
  fetchData();
  timer.value = setTimeout(() => {
    updateTable();
  }, 1000);
});
// 离开
onUnmounted(() => timer.value && clearTimeout(timer.value));
const oneLineCardRef = ref<any>(null);
const cardboxWidth = computed(() => (oneLineCardRef.value ? oneLineCardRef.value.$el.offsetWidth - 100 : 1200));

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
// 更新数据表
const updateTable = async () => {
  await upCodeTable({ id: 0 });
  await fetchData();
  Message.success({ content: '更新成功！', id: 'upStatus', duration: 2000 });
};
const addTable = async () => {
  console.log('addTable');
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
    const res = await upStatus({ id: record.id, status: record.status });
    if (res) {
      Message.success({ content: '更新状态成功', id: 'upStatus' });
    }
  } catch (error) {}
};
// 删除数据
const handleDel = async (record: any) => {
  try {
    const res = await del({ id: record.id, is_install: record.is_install });
    if (res) {
      await fetchData();
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
    label: '禁用',
    value: 1
  }
]);
// 打开代码生成器
const openCodeMaker = (record: any) => {
  router.push({ name: 'codemaker', query: { id: record.id } });
};
</script>

<style scoped lang="less">
.container {
  padding: 0 20px 20px 20px;
  height: 100%;
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

//添加底部说明
.tablebox {
  min-height: 496px;
}
//说明
.tigbox {
  .title {
    font-size: 16px;
    font-weight: 600;
  }
  .item {
    display: flex;
    margin-top: 10px;
    .label {
      color: var(--color-neutral-10);
    }
    .text {
      flex: 1;
      color: var(--color-neutral-6);
    }
  }
}
</style>
