<template>
  <div class="page-container">
    <ACard ref="oneLineCardRef" class="general-card oneLineCard" style="height: 100%">
      <div class="maker-rawer">
        <ASplit v-model:size="atrrSize" :style="{ height: 'calc(100vh - 125px)', width: '100%', overflow: 'hidden' }">
          <template #resize-trigger-icon>
            <span class="drag-icon-center" @click.stop="handleChangeAtrr">
              <icon-caret-left v-if="openAtrr" class="selfsplit-trigger-icon" />
              <icon-caret-right v-else class="selfsplit-trigger-icon" />
            </span>
          </template>
          <template #first>
            <!--表单字段-->
            <div class="maker-content flex flex-flow flex-between">
              <div class="header header-table">
                <div class="title">字段设置</div>
              </div>
              <div class="content flex flex-flow flex-between">
                <div class="table-box">
                  <div class="title">1.表单字段</div>
                  <div class="table-main">
                    <ATable
                      :columns="columnsfiles"
                      :data="field_list"
                      :pagination="false"
                      size="small"
                      :draggable="{ type: 'handle', width: 40 }"
                      :scroll="{ y: `${(cardboxHeight - 50) / 2 - 30}px` }"
                      :scrollbar="true"
                      @change="handleChangeDragField"
                    >
                      <template #drag-handle-icon>
                        <icon-drag-arrow />
                      </template>
                      <template #isform="{ rowIndex }">
                        <ACheckbox v-model="field_list[rowIndex].isform" />
                      </template>
                      <template #required="{ rowIndex }">
                        <ACheckbox v-model="field_list[rowIndex].required" />
                      </template>
                      <template #name="{ rowIndex }">
                        <AInput
                          v-model="field_list[rowIndex].name"
                          placeholder="填写字段名称"
                          @input="handleinputForm(field_list[rowIndex])"
                        />
                      </template>
                      <template #formtype="{ record }">
                        <ASelect v-model="record.formtype" placeholder="请选择" allow-search>
                          <AOption value="text">文本框</AOption>
                          <AOption value="number">数字本文</AOption>
                          <AOption value="textarea">文本域</AOption>
                          <AOption value="editor">富文本</AOption>
                          <AOption value="select">下拉框</AOption>
                          <AOption value="radio">单选框</AOption>
                          <AOption value="checkbox">复选框</AOption>
                          <AOption value="date">日期控件</AOption>
                          <AOption value="datetime">日期时间控件</AOption>
                          <AOption value="time">时间选择器</AOption>
                          <AOption value="image">单图上传</AOption>
                          <AOption value="images">多图上传</AOption>
                          <AOption value="file">单文件上传</AOption>
                          <AOption value="files" disabled>多文件上传</AOption>
                        </ASelect>
                      </template>
                      <template #datatable="{ record }">
                        <ASelect
                          v-if="record.formtype == 'select'"
                          v-model="record.datatable"
                          allow-search
                          allow-clear
                          placeholder="请选择"
                          @change="getTableField"
                        >
                          <AOption
                            v-for="item in tablelist"
                            :key="item.name"
                            :value="item.name"
                            :title="item.name + ' ' + item.title"
                          >
                            {{ item.name }}
                          </AOption>
                        </ASelect>
                      </template>
                      <template #datatablename="{ record }">
                        <ASelect
                          v-if="record.formtype == 'select' && record.datatable != ''"
                          v-model="record.datatablename"
                          allow-search
                          allow-clear
                          placeholder="请选择"
                          @popup-visible-change="
                            (val: any) => {
                              val ? getTableField(record.datatable) : null;
                            }
                          "
                        >
                          <AOption
                            v-for="item in fieldList[record.datatable]"
                            :key="item['value']"
                            :value="item['value']"
                          >
                            {{ item['value'] }}
                          </AOption>
                        </ASelect>
                      </template>
                    </ATable>
                  </div>
                </div>
                <div class="table-box">
                  <div class="title">2.列表展示字段</div>
                  <div class="table-main">
                    <ATable
                      :columns="columnslist"
                      :data="list"
                      :pagination="false"
                      size="small"
                      :draggable="{ type: 'handle', width: 40 }"
                      :scroll="{ y: `${(cardboxHeight - 50) / 2 - 30}px` }"
                      :scrollbar="true"
                      @change="handleChangeDragList"
                    >
                      <template #drag-handle-icon>
                        <icon-drag-arrow />
                      </template>
                      <template #name="{ rowIndex }">
                        <AInput
                          v-model="list[rowIndex].name"
                          placeholder="填写字段名称"
                          @input="handleinputForm(list[rowIndex])"
                        />
                      </template>
                      <template #islist="{ rowIndex }">
                        <ACheckbox v-model="list[rowIndex].islist" />
                      </template>
                      <template #isorder="{ rowIndex }">
                        <ACheckbox v-model="list[rowIndex].isorder" />
                      </template>
                      <template #align="{ record }">
                        <ASelect v-model="record.align" placeholder="选择对齐方式">
                          <AOption value="left">左边对齐</AOption>
                          <AOption value="center">居中对齐</AOption>
                          <AOption value="right">右边对齐</AOption>
                        </ASelect>
                      </template>
                      <template #width="{ rowIndex }">
                        <AInputNumber v-model="list[rowIndex].width" placeholder="空或0表示不设置" />
                      </template>
                    </ATable>
                  </div>
                </div>
              </div>
            </div>
          </template>
          <template #second>
            <!--属性-->
            <div class="maker-content">
              <div class="header">
                <ATabs v-model:active-key="TabsIndex" class="htabs" :hide-content="false">
                  <ATabPane :key="1" title="基本设置" />
                  <ATabPane :key="2" title="搜索字段" />
                  <ATabPane :key="3" title="模板类型" />
                </ATabs>
              </div>
              <div class="content">
                <AScrollbar style="overflow: auto" :style="{ height: `${cardboxHeight - 40}px` }">
                  <div v-if="codedata" class="formbox">
                    <AForm ref="formRef" :model="codedata" auto-label-width>
                      <div v-show="TabsIndex == 1" class="form-rawer">
                        <AFormItem field="comment" label="表名:" validate-trigger="input">
                          <span class="textbox">{{ codedata.tablename }}</span>
                        </AFormItem>
                        <AFormItem
                          label="上级菜单"
                          field="pid"
                          style="margin-bottom: 15px"
                          :rules="[{ required: true, message: '请填上级菜单' }]"
                        >
                          <ATreeSelect
                            v-model="codedata.pid"
                            placeholder="选择上级菜单"
                            :data="parntList"
                            :field-names="{ key: 'id', title: 'title', children: 'children' }"
                            @change="handleChangeMenu"
                          ></ATreeSelect>
                          <template #extra>
                            <div>
                              若绑定到新的目录请到
                              <ALink href="/#/system/rule">菜单管理</ALink>
                              添加新目录
                            </div>
                          </template>
                        </AFormItem>
                        <AFormItem label="菜单图标" field="icon" style="margin-bottom: 15px">
                          <AInputSearch v-model="codedata.icon" placeholder="选择图标/填写" search-button>
                            <template v-if="codedata.icon" #prefix>
                              <Icon :icon="codedata.icon" />
                            </template>
                            <template #button-icon>
                              <APopover position="br" trigger="click">
                                <icon-apps :size="23" />
                                <template #content>
                                  <IconPicker @change="handleIcon"></IconPicker>
                                </template>
                              </APopover>
                            </template>
                          </AInputSearch>
                        </AFormItem>
                        <AFormItem
                          field="rule_name"
                          label="菜单名称:"
                          validate-trigger="input"
                          :rules="[{ required: true, message: '请填写菜单名称' }]"
                        >
                          <AInput v-model="codedata.rule_name" placeholder="请填菜单名称" />
                        </AFormItem>
                        <AFormItem
                          field="routePath"
                          label="路由Path"
                          validate-trigger="input"
                          :rules="[{ required: true, message: '请填写路由路由（path）' }]"
                        >
                          <AInput v-model="codedata.routePath" placeholder="请填路由（path）" />
                          <template #extra>
                            <div>如果是根目录或访问路由不加上级目录在名称前加/</div>
                          </template>
                        </AFormItem>
                        <AFormItem
                          field="routeName"
                          label="路由name"
                          validate-trigger="input"
                          :rules="[{ required: true, message: '请填写路由路由（name）' }]"
                        >
                          <AInput v-model="codedata.routeName" placeholder="请填路由（name）" />
                        </AFormItem>
                        <AFormItem
                          field="component"
                          label="前端组件路径"
                          validate-trigger="input"
                          :rules="[{ required: true, message: '请填写前端组件路径' }]"
                        >
                          <AInput v-model="codedata.component" placeholder="请填前端组件路径" />
                        </AFormItem>
                        <AFormItem
                          label="后台代码路径"
                          :content-flex="false"
                          :merge-props="false"
                          :rules="[{ required: true, message: '请填后台代码路径径' }]"
                        >
                          <ARow>
                            <ACol :span="13">
                              <AFormItem field="api_path" validate-trigger="input" no-style>
                                <AInput v-model="codedata.api_path" placeholder="后台代码路径" />
                              </AFormItem>
                            </ACol>
                            <ACol :span="1">
                              <div class="flex-all-center" style="height: 32px">/</div>
                            </ACol>
                            <ACol :span="10">
                              <AFormItem field="api_filename" validate-trigger="input" no-style>
                                <AInput v-model="codedata.api_filename" placeholder="代码文件名称" />
                              </AFormItem>
                            </ACol>
                          </ARow>
                          <template #extra>
                            <div>
                              后台代码在
                              <span class="textbox">{{ codedata.api_path + '/' + codedata.api_filename }}</span>
                              文件下
                            </div>
                          </template>
                        </AFormItem>
                      </div>
                      <div v-show="TabsIndex == 2" class="form-rawer">
                        <div class="seachtable">
                          <ATable
                            :columns="columnsseach"
                            :data="search_list"
                            :pagination="false"
                            size="small"
                            :draggable="{ type: 'handle', width: 40 }"
                            :scroll="{ y: `${cardboxHeight - 50 - 30}px` }"
                            :scrollbar="true"
                            @change="handleChangeDragSearch"
                          >
                            <template #drag-handle-icon>
                              <icon-drag-arrow />
                            </template>
                            <template #name="{ rowIndex }">
                              <AInput v-model="search_list[rowIndex].name" placeholder="填写字段名称" />
                            </template>
                            <template #issearch="{ rowIndex }">
                              <ACheckbox v-model="search_list[rowIndex].issearch" />
                            </template>
                            <template #searchway="{ record }">
                              <ASelect v-model="record.searchway" placeholder="请选择">
                                <AOption value="=">=</AOption>
                                <AOption value="!=">!=</AOption>
                                <AOption value=">">></AOption>
                                <AOption value=">=">>=</AOption>
                                <AOption value="<">&lt;</AOption>
                                <AOption value="<=">&lt;=</AOption>
                                <AOption value="like">Like</AOption>
                                <AOption value="Between">Between</AOption>
                              </ASelect>
                            </template>
                            <template #searchtype="{ rowIndex }">
                              <ASelect v-model="search_list[rowIndex].searchtype" placeholder="请选择">
                                <AOption value="text">文本框</AOption>
                                <AOption value="select">下拉框</AOption>
                                <AOption value="date">日期选择</AOption>
                                <AOption value="daterange" :disabled="search_list[rowIndex].searchway != 'Between'">
                                  日期范围选择
                                </AOption>
                              </ASelect>
                            </template>
                          </ATable>
                        </div>
                      </div>
                      <div v-show="TabsIndex == 3" class="form-rawer">
                        <ARadioGroup v-model="codedata.tpl_type">
                          <div class="tpllist">
                            <div
                              v-for="item in tpllist"
                              :key="item.type"
                              class="tpl-item"
                              @click="codedata.tpl_type = item.type"
                            >
                              <div class="tpl-wrap">
                                <div class="tpl-img">
                                  <ACarousel indicator-type="never" :style="{ width: '100%', height: '180px' }">
                                    <ACarouselItem v-for="image in item.images" :key="image">
                                      <img :src="image" :style="{ height: '100%' }" alt="" />
                                    </ACarouselItem>
                                  </ACarousel>
                                </div>
                                <div class="tlp-option">
                                  <ARadio :value="item.type">
                                    <div class="title">{{ item.title }}</div>
                                  </ARadio>
                                </div>
                              </div>
                            </div>
                          </div>
                        </ARadioGroup>
                      </div>
                    </AForm>
                  </div>
                </AScrollbar>
              </div>
            </div>
          </template>
        </ASplit>
      </div>
    </ACard>
    <div class="actions">
      <ASpace>
        <AButton @click="onReback">返回列表</AButton>
        <AButton
          v-if="codedata.is_install == 1"
          type="primary"
          status="danger"
          :loading="uninstallloading"
          @click="handleUninstall"
        >
          卸载代码
        </AButton>
        <AButton type="primary" :loading="loading" @click="onSubmitClick">
          {{ codedata.is_install ? '重新生成' : '立即生成' }}
        </AButton>
      </ASpace>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue';
import type { FormInstance } from '@arco-design/web-vue';
// api
import type { CodeListItem, CodedataItem, TreeItem } from '@/api/developer/generatecode';
import { getContent, getdbfield, save, uninstallcode } from '@/api/developer/generatecode';
import type { TableItem } from '@/api/developer/devapi';
import { getTables } from '@/api/developer/devapi';
import type { RuleItem } from '@/api/system/rule';
import { getParent } from '@/api/system/rule';
import { useAppStore } from '@/store';
import useLoading from '@/hooks/loading';
import { Icon, IconPicker } from '@/components/Icon';
import { columnsfiles, columnslist, columnsseach } from './data';
const appStore = useAppStore();
const route = useRoute();
const router = useRouter();
const props = defineProps({});
const atrrSize = ref(0.7);
const oneLineCardRef = ref<any>(null);
const TabsIndex = ref(1);
const codedata = ref<CodedataItem>({
  id: 0,
  tablename: '',
  comment: '',
  pid: 0,
  rule_id: 0,
  rule_name: '',
  icon: '',
  is_install: 0,
  routePath: '',
  routeName: '',
  component: '',
  api_path: '',
  api_filename: '',
  tpl_type: 'list',
  cate_tablename: ''
});
const id_prod = import.meta.env.VITE_APP_ENV == 'production';
const parntList = ref<RuleItem[]>([]);
const tablelist = ref<TableItem[]>([]);
const modelroot = ref('');
onMounted(async () => {
  // appStore.footer=false
  await getpageData();
  const resultdata = await getParent({});
  tablelist.value = await getTables({});
  const parntList_df: any = [{ id: 0, title: '一级菜单', pid: 0, locale: '' }];
  if (resultdata) {
    parntList.value = parntList_df.concat(resultdata);
  } else {
    parntList.value = [];
  }
});
watch(props, () => {});
// 离开
onUnmounted(() => {
  appStore.footer = true;
});
// 获取页面数据
const field_list = ref<CodeListItem[]>([]);
const list = ref<CodeListItem[]>([]);
const search_list = ref<CodeListItem[]>([]);

function sortByFields(arr: any[], fields: string[]) {
  if (!arr || !fields || fields.length === 0) {
    return arr;
  }
  return arr.sort((a: any, b: any) => {
    for (const field of fields) {
      if (a[field] < b[field]) {
        return -1;
      }
      if (a[field] > b[field]) {
        return 1;
      }
    }
    return 0;
  });
}

const getpageData = async () => {
  const mdata = await getContent({ id: route.query.id });
  codedata.value = mdata.data;
  field_list.value = sortByFields(mdata.list, ['field_weigh', 'id']);
  list.value = sortByFields(mdata.list, ['list_weigh', 'id']);
  search_list.value = sortByFields(mdata.list, ['search_weigh', 'id']);
};
const openAtrr = ref(false);
const handleChangeAtrr = () => {
  openAtrr.value = !openAtrr.value;
  atrrSize.value = openAtrr.value ? 0.7 : 1;
};
// 获取表字段
const fieldList = ref<TreeItem[][]>([]);
const getTableField = async (value: any) => {
  if (value) {
    fieldList.value[value] = await getdbfield({ tablename: value });
  } else {
    fieldList.value = [];
  }
};
// 返回
const onReback = () => {
  router.go(-1);
};
// 生成表单
const formRef = ref<FormInstance>();
const { loading, setLoading } = useLoading();
const onSubmitClick = async () => {
  if (id_prod) {
    Message.error({
      content: 'Go属于编译语言，生产环境无法修改代码，请您在开发环境使用！',
      id: 'upStatus',
      duration: 2000
    });
    return;
  }
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);

      // 合并三个list

      const listMap = list.value.reduce((acc, item) => {
        acc.set(item.field, item);
        return acc;
      }, new Map<string, CodeListItem>());

      const searchListMap = search_list.value.reduce((acc, item) => {
        acc.set(item.field, item);
        return acc;
      }, new Map<string, CodeListItem>());

      field_list.value.forEach(a => {
        const lf = listMap.get(a.field);
        const sf = searchListMap.get(a.field);

        a.field_weigh = a.field_weigh || a.id;

        a.islist = lf ? lf.islist : false;
        a.isorder = lf ? lf.isorder : false;
        a.align = lf ? lf.align : 'left';
        a.width = lf ? lf.width : 0;
        a.list_weigh = lf ? lf.list_weigh || lf.id : 0;

        a.issearch = sf ? sf.issearch : false;
        a.searchway = sf ? sf.searchway : '=';
        a.searchtype = sf ? sf.searchtype : 'text';
        a.search_weigh = sf ? sf.search_weigh || sf.id : 0;
      });

      await save({
        codeData: codedata.value,
        list: field_list.value
      });
      Message.success({
        content: '生成成功',
        id: 'upStatus',
        duration: 2000
      });
      setLoading(false);
    } else {
      Message.error('请填写必填项');
    }
  } catch (error) {
    console.error(error);
    setLoading(false);
    Message.error({ content: '', id: 'upStatus', duration: 2 });
  }
};
// 菜单改变
const handleChangeMenu = (val: any) => {
  const ruledata = parntList.value.find(item => item.id == val);
  if (ruledata) {
    modelroot.value = ruledata.routePath;
  }
  WatchChangPath(codedata.value);
};
const WatchChangPath = (data: any) => {
  const tanme_arr = data.tablename.split('_');
  const apiHost = import.meta.env.VITE_API_HOST;
  if (tanme_arr && tanme_arr.length == 3) {
    codedata.value.cate_tablename = `${tanme_arr[0]}_${tanme_arr[1]}_cate`;
    // 父级菜单
    const ruledatas = parntList.value.find(item => item.routePath == `/${tanme_arr[1]}`);
    if (ruledatas) {
      codedata.value.pid = ruledatas.id;
    }
  }
  if (tanme_arr && tanme_arr.length == 3) {
    codedata.value.routePath = `${tanme_arr[2]}`;
    codedata.value.routeName = `${tanme_arr[2]}`;
    codedata.value.component = `${
      modelroot.value ? modelroot.value.split('/')[1] : tanme_arr[1]
    }/${tanme_arr[2]}/index`;
    codedata.value.api_path = `${apiHost}/${modelroot.value ? modelroot.value.split('/')[1] : tanme_arr[1]}`;
    codedata.value.api_filename = `${tanme_arr[2]}.go`;
  } else {
    codedata.value.routePath = `${tanme_arr[1]}`;
    codedata.value.routeName = `${tanme_arr[1]}`;
    codedata.value.component = `${modelroot.value ? modelroot.value.split('/')[1] : 'xx'}/${tanme_arr[1]}/index`;
    codedata.value.api_path = `${apiHost}/${modelroot.value ? modelroot.value.split('/')[1] : 'xx'}`;
    codedata.value.api_filename = `${tanme_arr[1]}.go`;
  }
};
// 卸载
const uninstallloading = ref(false);
const handleUninstall = async () => {
  if (id_prod) {
    Message.error({
      content: 'Go属于编译语言，生产环境无法修改代码，请您在开发环境使用！',
      id: 'upStatus',
      duration: 2000
    });
    return;
  }
  try {
    uninstallloading.value = true;

    const res = await uninstallcode({ id: route.query.id });
    uninstallloading.value = false;
    if (res) {
      codedata.value.is_install = 0;
      Message.success({ content: '卸载成功', id: 'upStatus' });
    }
  } catch (error) {
    uninstallloading.value = false;
    Message.error({ content: '', id: 'upStatus', duration: 2 });
  }
};
// 选择图标
const handleIcon = (icon: any) => {
  codedata.value.icon = icon;
};
// 拖拽排序
const handleChangeDragField = (_data: any) => {
  _data.forEach((item: any, index: any) => {
    item.field_weigh = index + 1;
  });
  field_list.value = _data;
};
const handleChangeDragList = (_data: any) => {
  _data.forEach((item: any, index: any) => {
    item.list_weigh = index + 1;
  });
  list.value = _data;
};
const handleChangeDragSearch = (_data: any) => {
  _data.forEach((item: any, index: any) => {
    item.search_weigh = index + 1;
  });
  search_list.value = _data;
};
// 表单修改名称
const handleinputForm = (data: any) => {
  const fielddata = field_list.value.filter(item => {
    return item.id == data.id;
  });
  fielddata[0].name = data.name;
  const searchdata = search_list.value.filter(item => {
    return item.id == data.id;
  });
  searchdata[0].name = data.name;
};
// 列表修改名称
const handleinputList = (data: any) => {
  const listdata = list.value.filter(item => {
    return item.id == data.id;
  });
  listdata[0].name = data.name;
  const searchdata = search_list.value.filter(item => {
    return item.id == data.id;
  });
  searchdata[0].name = data.name;
};
const GetAssetsFile = (url: string) => {
  return new URL(`../../../assets/images/${url}`, import.meta.url).href;
};
// 模板列表
const dfimg = ref(GetAssetsFile('codetpl.png'));
const tpllist = ref([
  {
    title: '简单数据列表,没有富文本',
    type: 'list',
    images: [dfimg.value]
  },
  {
    title: '富文本数据列表,带有富文本',
    type: 'contentlist',
    images: [dfimg.value]
  },
  {
    title: '富文本数据带有分类数据,带有富文本，并有侧边分类数据',
    type: 'contentcatelist',
    images: [dfimg.value]
  }
]);
</script>

<style lang="less" scoped>
.page-container {
  border-radius: 4px;
  padding: 10px 10px 20px;
  height: 100%;
  .maker-rawer {
    height: 100%;
    .maker-content {
      height: 100%;
      width: 100%;
      .header {
        height: 40px;
        //.htabs {
        //  // padding-top: 10px;
        //}
      }
      .header-table {
        border-bottom: var(--color-neutral-3) solid 1px;
        display: flex;
        align-items: center;
        .title {
          padding-left: 15px;
          color: var(--color-neutral-8);
          font-size: 16px;
        }
      }
      .content {
        flex: 1;
        width: 100%;
        .table-box {
          flex: 1;
          padding: 0 10px;
          .title {
            padding-left: 15px;
            height: 30px;
            display: flex;
            align-items: center;
          }
          //.table-main {
          //}
        }
        .formbox {
          padding: 10px;
          .form-rawer {
            .textbox {
              color: var(--color-neutral-6);
            }
          }
        }
        //模板列表
        .tpllist {
          width: 100%;
          height: 100%;
          .tpl-item {
            cursor: pointer;
            margin-bottom: 10px;
            .tpl-wrap {
              width: calc(100% - 2px);
              height: calc(100% - 2px);
              border: 1px solid #f5f5fa;
              border-radius: 3px;
              user-select: none;
              overflow: hidden;
              padding: 10px;
              .tpl-img {
                height: 180px;
                border-radius: 3px;
                overflow: hidden;
              }
              .tlp-option {
                margin-top: 10px;
              }
            }
          }
        }
      }
    }
  }
  //提交按钮
  .actions {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    height: 50px;
    padding: 10px;
    background: var(--color-bg-2);
    text-align: right;
  }
}
//设置tab
:deep(.arco-tabs-nav-tab-list) {
  width: 100%;
  display: flex;
  justify-content: center;
}
:deep(.arco-tabs-nav-type-line .arco-tabs-tab) {
  flex: 1;
  text-align: center;
  align-self: center;
  justify-content: center;
}
//设置car
:deep(.arco-card-size-medium .arco-card-body) {
  height: 100%;
  padding: 0;
}
:deep(.arco-carousel-item-current) {
  text-align: center;
}
//移动图标
.drag-icon-center {
  background-color: rgb(var(--arcoblue-6));
  border-radius: 2px 0 0 2px;
  cursor: pointer;
  width: 5px;
  height: 40px;
  display: flex;
  user-select: none;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 14px;
}
.selfsplit-trigger-icon {
  display: inline-block;
  margin: -3px;
}
</style>
