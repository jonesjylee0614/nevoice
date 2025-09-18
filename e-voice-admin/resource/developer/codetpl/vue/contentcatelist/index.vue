<template>
  <div class="container" >
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <ACard class="general-card oneLineCard" ref="oneLineCardRef" style="height: calc(100% - 50px);">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16" >
          <ASpace>
            <AInput :style="{width:'160px'}"  v-model="formModel.title" placeholder="名称" allow-clear />
            <ARangePicker v-model="formModel.createdTime" :style="{width:'200px'}" />
            <ASelect v-model="formModel.status"  :options="statusOptions" placeholder="状态" :style="{width:'120px'}" />
            <AButton type="primary" :loading="btnLoading" @click="search">
              <template #icon>
                <icon-search />
              </template>
              查询
            </AButton>
            <AButton @click="reset">
              重置
            </AButton>
          </ASpace>
        </ACol>
        <ACol
          :span="8"
           style="text-align: right;"
        >
        <ASpace>
          <AButton type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新建
          </AButton>
          <AButton  @click="handleManager">管理分类</AButton>
          <ATooltip content="刷新">
            <div class="action-icon" @click="search"
              ><icon-refresh size="18"
            /></div>
          </ATooltip>
          </ASpace>
        </ACol>
      </ARow>
      <ATable
         row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="cloneColumns"
        :data="renderData"
        :bordered="{wrapper:true,cell:true}"
        :size="size"
        :default-expand-all-rows="true"
        :scroll="{x:cardboxWidth}"
        @page-change="handlePaageChange" 
        @page-size-change="handlePageSizeChange"
      >
        <template #name="{ record }">
         {{ record.name }}<span v-if="record.nickname" style="padding-left: 5px;color: var(--color-neutral-4);">{{ record.nickname }}</span>
        </template>
        <template #image="{ record }">
            <img
              alt=""
              style="height: 50px;border-radius: 5px;"
              :src="record.image"
            />
        </template>
        <template #createTime="{record,column}">
          {{record[column.dataIndex]>0?dayjs(record[column.dataIndex]*1000).format("YYYY-MM-DD"):"--"}}
        </template>
        <template #status="{ record }">
          <ASwitch type="round" v-model="record.status" :checked-value="0" :unchecked-value="1" @change="handleStatus(record)">
              <template #checked>
                开
              </template>
              <template #unchecked>
                关
              </template>
            </ASwitch>
        </template>
        <template #operations="{ record }">
          <ASpace class="option">
            <Icon icon="icon-edit" color="rgb(var(--primary-6))" @click="handleEdit(record)" />
            <APopconfirm content="您确定要删除吗?" @ok="handleDel(record)">
              <Icon icon="icon-delete" :size="18" color="#ed6f6f"/>
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!--表单-->
    <AddForm @register="registerModal" @success="handleData"/>
    <CateIndex @register="registerCateIndexModal" @success="handleData"/>
  </div>
</template>

<script lang="ts" setup>
  import useLoading from '@/hooks/loading';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
  import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
  import cloneDeep from 'lodash/cloneDeep';
  import { getList,upStatus,del} from './api';
  import { columns} from './data';
  import dayjs from 'dayjs';
  import { useModal } from '@/components/Modal';
  import AddForm from './AddForm.vue';
  import CateIndex from './cate/index.vue';
  import { useI18n } from 'vue-i18n';
  import {Icon} from '@/components/Icon';
  import { Message } from '@arco-design/web-vue';
  import { Pagination } from '@/types/global';
  import { useRoute } from 'vue-router'
  const route = useRoute();
  const { t } = useI18n();
  const [registerModal, { openModal }] = useModal();
  const [registerCateIndexModal, { openModal:cateModdal }] = useModal();
  const oneLineCardRef = ref(null);
  const cardboxWidth= computed(() => (oneLineCardRef.value ? oneLineCardRef.value["$el"]["offsetWidth"] -100: 1200));
  //分页
  const basePagination: Pagination = {
    current: 1,
    pageSize: 10,
  };
  const pagination = reactive({
    ...basePagination,
    showTotal:true,
    showPageSize:true,
  });
  type SizeProps = 'mini' | 'small' | 'medium' | 'large';
  type Column = TableColumnData & { checked?: true };
  const { loading, setLoading } = useLoading(true);
  const { loading: btnLoading, setLoading: setBtnLoading } = useLoading(false);
  const renderData = ref([]);
  const cloneColumns = ref<Column[]>([]);
  const showColumns = ref<Column[]>([]);
  const size = ref<SizeProps>('large');
   const generateFormModel = () => {
    return {
      trade_no: '',
      title: '',
      name: '',
      createdTime: [],
      status: '',
    };
  };
  const formModel = ref(generateFormModel());
  const fetchData = async () => {
    setLoading(true);
    try {
      const data= await getList({page:pagination.current,pageSize:pagination.pageSize,...formModel.value});
      renderData.value = data.items;
      pagination.current = data.page;
      pagination.total = data.total;
    } catch (err) {
      // you can report use errorHandler or other
    } finally {
      setLoading(false);
    }
  };
  //组件挂载完成后执行的函数
  onMounted(()=>{
    })
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
  const handleSelectDensity = (
    val: string | number | Record<string, any> | undefined,
    e: Event
  ) => {
    size.value = val as SizeProps;
  };

  watch(
    () => columns.value,
    (val) => {
      cloneColumns.value = cloneDeep(val);
      cloneColumns.value.forEach((item, index) => {
        item.checked = true;
      });
      showColumns.value = cloneDeep(cloneColumns.value);
    },
    { deep: true, immediate: true }
  );
  //管理分类
  const handleManager=()=>{
    cateModdal(true, {
      isUpdate: false,
      record:null
    });
  }
  //添加
  const handleCreate=()=>{
    openModal(true, {
      isUpdate: false,
      record:null
    });
  }
  //编辑数据
  const handleEdit=async(record:any)=>{
    openModal(true, {
      isUpdate: true,
      record:record
    });
  }
  //更新数据
  const handleData=async()=>{
    fetchData();
  }
  //分页
  const handlePaageChange = (page:any) => {
    pagination.current=page
    fetchData();
  }
  //分页总数
  const handlePageSizeChange = (pageSize:any) => {
    pagination.pageSize=pageSize
    fetchData();
  }
  //更新状态
  const handleStatus=async(record:any)=>{
    try {
        Message.loading({content:"更新状态中",id:"upStatus"})
       const res= await upStatus({id:record.id,status:record.status});
       if(res){
         Message.success({content:"更新状态成功",id:"upStatus"})
       }
    }catch (error) {
      Message.clear("top")
    } 
  }
  //删除数据
  const handleDel=async(record:any)=>{
    try {
        Message.loading({content:"删除中",id:"upStatus"})
       const res= await del({ids:[record.id]});
       if(res){
        fetchData();
         Message.success({content:"删除成功",id:"upStatus"})
       }
    }catch (error) {
      Message.clear("top")
    } 
}
  //状态
  const statusOptions = computed<SelectOptionData[]>(() => [
    {
      label: "全部",
      value: "",
    },
    {
      label: "正常",
      value: 0,
    },
    {
      label: "隐藏",
      value: 1,
    },
  ]);
</script>

<script lang="ts">
  export default {
    name: 'article',
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
  :deep(.general-card > .arco-card-header){
    padding: 10px 16px;
  }
  .option .arco-icon{
    user-select: none;
    cursor: pointer;
    opacity: .8;
    &:hover{
      opacity: 1;
    }
  }
</style>
