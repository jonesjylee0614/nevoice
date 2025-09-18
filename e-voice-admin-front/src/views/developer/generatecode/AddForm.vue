<template>
  <BasicModal
    v-bind="attrs"
    :footer="false"
    :mask-closable="false"
    :is-padding="false"
    :loading="loading"
    width="1000px"
    :min-height="modelHeight"
    :title="getTitle"
    @register="registerModal"
    @height-change="onHeightChange"
    @ok="handleSubmit"
  >
    <div class="addFormbox" :style="{ 'min-height': `${windHeight}px` }">
      <div class="tabs-content">
        <div class="content_box">
          <!--基础信息-->
          <AForm ref="formRef" :model="formData" auto-label-width>
            <div v-show="activeKey == 1" class="gcodebox">
              <ARow :gutter="16">
                <ACol :span="12">
                  <AFormItem field="comment" label="表说明:" validate-trigger="input">
                    <span class="textbox">{{ formData.comment }}</span>
                  </AFormItem>
                </ACol>
                <ACol :span="12">
                  <AFormItem field="tablename" label="表名:" validate-trigger="input">
                    <span class="textbox">{{ formData.tablename }}</span>
                  </AFormItem>
                </ACol>
                <ACol :span="12">
                  <AFormItem
                    label="上级菜单"
                    field="pid"
                    style="margin-bottom: 15px"
                    :rules="[{ required: true, message: '请填上级菜单' }]"
                  >
                    <ATreeSelect
                      v-model="formData.pid"
                      placeholder="选择上级菜单"
                      :data="parntList"
                      :field-names="{
                        key: 'id',
                        title: 'title',
                        children: 'children'
                      }"
                      @change="handleChangeMenu"
                    ></ATreeSelect>
                    <template #extra>
                      <div>
                        若要绑定到新的目录请到
                        <ALink href="/#/system/rule">菜单管理</ALink>
                        添加新目录
                      </div>
                    </template>
                  </AFormItem>
                </ACol>
                <ACol :span="12">
                  <AFormItem label="图标" field="icon" style="margin-bottom: 15px">
                    <AInputSearch v-model="formData.icon" placeholder="选择图标/填写" search-button>
                      <template v-if="formData.icon" #prefix>
                        <Icon :icon="formData.icon" />
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
                </ACol>
                <ACol :span="12">
                  <AFormItem
                    field="routePath"
                    label="路由Path"
                    validate-trigger="input"
                    :rules="[{ required: true, message: '请填写路由路由（path）' }]"
                  >
                    <AInput v-model="formData.routePath" placeholder="请填路由（path）" />
                    <template #extra>
                      <div>如果是根目录或访问路由不加上级目录请在名称前加/</div>
                    </template>
                  </AFormItem>
                </ACol>
                <ACol :span="12">
                  <AFormItem
                    field="routeName"
                    label="路由name"
                    validate-trigger="input"
                    :rules="[{ required: true, message: '请填写路由路由（name）' }]"
                  >
                    <AInput v-model="formData.routeName" placeholder="请填路由（name）" />
                  </AFormItem>
                </ACol>
                <ACol :span="10">
                  <AFormItem
                    field="component"
                    label="前端组件路径"
                    validate-trigger="input"
                    :rules="[{ required: true, message: '请填写前端组件路径' }]"
                  >
                    <AInput v-model="formData.component" placeholder="请填前端组件路径" />
                  </AFormItem>
                </ACol>
                <ACol :span="14">
                  <AFormItem
                    field="api_path"
                    label="后台代码路径"
                    validate-trigger="input"
                    :rules="[{ required: true, message: '请填写后台代码路径' }]"
                  >
                    <AInput v-model="formData.api_path" placeholder="请填后台代码路径" />
                    <span style="width: 50px; text-align: center">文件</span>
                    <AInput v-model="formData.api_filename" style="width: 190px" placeholder="请填后台代码文件" />
                    <template #extra>
                      <div>
                        后台业务代码
                        <span class="textbox">{{ formData.api_path + '/' + formData.api_filename }}</span>
                        文件下
                      </div>
                    </template>
                  </AFormItem>
                </ACol>
                <ACol :span="24">
                  <AFormItem
                    field="fields"
                    label="查询列表字段"
                    validate-trigger="input"
                    :rules="[{ required: true, message: '请填写查询列表字段' }]"
                  >
                    <ASelect
                      v-model="formData.fields"
                      placeholder="选择查询列表字段"
                      multiple
                      :max-tag-count="12"
                      allow-clear
                    >
                      <AOption v-for="item in fieldList" :key="item.value" :value="item.value">
                        {{ item.label }}
                      </AOption>
                    </ASelect>
                  </AFormItem>
                </ACol>
                <ACol :span="12">
                  <AFormItem
                    field="tpl_type"
                    label="模板类型"
                    validate-trigger="input"
                    :rules="[{ required: true, message: '请选择模板类型' }]"
                  >
                    <ASelect v-model="formData.tpl_type" placeholder="选择模板类型" allow-clear @change="handelTplType">
                      <AOption value="list">数据列表</AOption>
                      <AOption value="contentlist">富文本数据列表</AOption>
                      <AOption value="contentcatelist">富文本数据关联分类</AOption>
                    </ASelect>
                  </AFormItem>
                </ACol>
                <ACol v-if="formData.tpl_type == 'contentcatelist'" :span="12">
                  <AFormItem
                    field="cate_tablename"
                    label="分类的数据库"
                    validate-trigger="input"
                    :rules="[{ required: true, message: '请选分类的数据库' }]"
                  >
                    <ASelect v-model="formData.cate_tablename" placeholder="选择分类的数据库" allow-clear>
                      <AOption v-for="item in tablenameList" :key="item.value" :value="item.value">
                        {{ item.label }}
                      </AOption>
                    </ASelect>
                  </AFormItem>
                </ACol>
                <ACol :span="24">
                  <div class="btnbox">
                    <ASpace>
                      <AButton
                        html-type="submit"
                        size="large"
                        type="primary"
                        shape="round"
                        style="width: 200px; margin-top: 15px"
                        @click="handleSubmit"
                      >
                        开始生成
                      </AButton>
                      <AButton
                        v-if="formData.is_install == 1"
                        size="large"
                        shape="round"
                        style="width: 200px; margin-top: 15px"
                        @click="handleUninstall"
                      >
                        卸载代码及菜单
                      </AButton>
                    </ASpace>
                  </div>
                </ACol>
              </ARow>
              <div class="tigmsg">
                <div>注意：</div>
                <span>
                  生成代码是您要再后端config/settings.yml配置中修改前端代码所在的目录vueobjroot=D:/Project/develop/vue/gofly_base/gofly_business(修改你前端代码路径)
                </span>
              </div>
            </div>
          </AForm>
        </div>
      </div>
    </div>
  </BasicModal>
</template>

<script lang="ts" setup>
import { cloneDeep, join } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
// api
import type { TreeItem } from '@/api/developer/generatecode';
import { get_tablelist, getdbfield, save, uninstallcode } from '@/api/developer/generatecode';
import type { RuleItem } from '@/api/system/rule';
import { getParent } from '@/api/system/rule';
import useLoading from '@/hooks/loading';
import { BasicModal, useModalInner } from '@/components/Modal';
import { Icon, IconPicker } from '@/components/Icon';

const attrs = useAttrs();
const emit = defineEmits(['success']);

const id_prod = import.meta.env.VITE_APP_ENV == 'production';
const parntList = ref<RuleItem[]>([]);
const fieldList = ref<TreeItem[]>([]);
const tablenameList = ref<TreeItem[]>([]);
const isUpdate = ref(false);
const activeKey = ref(1);
const modelHeight = ref(620);
const windHeight = ref(620);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  pid: '',
  comment: '',
  icon: '',
  tablename: '',
  engine: '',
  routePath: '',
  routeName: '',
  component: '',
  api_path: '',
  api_filename: '',
  fields: [],
  is_install: 0,
  tpl_type: 'list',
  cate_tablename: ''
};
const formData = ref<any>(basedata);
// 编辑器
const modelroot = ref('');
const codeData = ref();
const [registerModal, { closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  activeKey.value = 1;
  isUpdate.value = Boolean(data?.isUpdate);
  const resultdata = await getParent({});
  // const parntList_df : any=[{id: 0,title: "一级菜单",pid: 0,locale:""}];
  if (resultdata) {
    parntList.value = resultdata;
    const ruleData = parntList.value.find(item => item.id == data.record.pid);
    if (ruleData) {
      modelroot.value = ruleData.routePath;
    }
    if (data.record.tpl_type == 'cate') {
      tablenameList.value = await get_tablelist({
        id: formData.value.id
      });
    }
    // parntList.value=parntList_df.concat(resultdata)
  } else {
    parntList.value = [];
  }
  if (unref(isUpdate)) {
    formData.value = cloneDeep(data.record);
    if (formData.value.fields) {
      formData.value.fields = formData.value.fields.split(',');
    }
    if (data.record.pid == 0) {
      formData.value.pid = '';
    }
    // 生成路径
    WatchChangPath(data);
    codeData.value = data;
  } else {
    formData.value = cloneDeep(basedata);
  }
  // 最好加载一下数据表字段
  setTimeout(async () => {
    fieldList.value = await getdbfield({
      tablename: data.record.tablename
    });
  }, 1000);
});
// 菜单改变
const handleChangeMenu = (val: any) => {
  const ruledata = parntList.value.find(item => item.id == val);
  if (ruledata) {
    modelroot.value = ruledata.routePath;
  }
  WatchChangPath(codeData.value);
};
const WatchChangPath = (data: any) => {
  const tanme_arr = data.record.tablename.split('_');
  const apiHost = import.meta.env.VITE_API_HOST;
  if (tanme_arr && tanme_arr.length == 3) {
    formData.value.cate_tablename = `${tanme_arr[0]}_${tanme_arr[1]}_cate`;
    // 父级菜单
    const ruledatas = parntList.value.find(item => item.routePath == `/${tanme_arr[1]}`);
    if (ruledatas) {
      formData.value.pid = ruledatas.id;
    }
  }
  if (tanme_arr && tanme_arr.length == 3) {
    formData.value.routePath = `${tanme_arr[2]}`;
    formData.value.routeName = `${tanme_arr[2]}`;
    formData.value.component = `${
      modelroot.value ? modelroot.value.split('/')[1] : tanme_arr[1]
    }/${tanme_arr[2]}/index`;
    formData.value.api_path = `${apiHost}/${modelroot.value ? modelroot.value.split('/')[1] : tanme_arr[1]}`;
    formData.value.api_filename = `${tanme_arr[2]}.go`;
  } else {
    formData.value.routePath = `${tanme_arr[1]}`;
    formData.value.routeName = `${tanme_arr[1]}`;
    formData.value.component = `${modelroot.value ? modelroot.value.split('/')[1] : 'xx'}/${tanme_arr[1]}/index`;
    formData.value.api_path = `${apiHost}/${modelroot.value ? modelroot.value.split('/')[1] : 'xx'}`;
    formData.value.api_filename = `${tanme_arr[1]}.go`;
  }
};
const getTitle = computed(() => (!unref(isUpdate) ? '后台代码生成管理' : '后台代码生成管理'));
// 点击确认
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
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

      const savedata = cloneDeep(unref(formData));
      savedata.fields = join(savedata.fields);
      const markedata = ref<TreeItem[]>([]);
      formData.value.fields.forEach((item: any) => {
        // console.log("日志：",item)
        const mdata = fieldList.value.find(data => data.value == item);
        // console.log("日志1：",mdata)
        if (mdata) {
          markedata.value.push(mdata);
        }
      });
      savedata.tablefieldname = markedata.value;
      await save(savedata);
      Message.success({
        content: '生成成功',
        id: 'upStatus',
        duration: 2000
      });
      closeModal();
      emit('success');
      setLoading(false);
    }
  } catch (error) {
    console.error(error);
    setLoading(false);
    Message.success({ content: '生成功', id: 'upStatus', duration: 10 });
  }
};
// 监听高度
const onHeightChange = (val: any) => {
  windHeight.value = val;
};
// 卸载
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
    const res = await uninstallcode({ id: formData.value.id });
    if (res) {
      formData.value.is_install = 0;
      Message.success({ content: '卸载成功', id: 'upStatus' });
    }
  } catch (error) {
    Message.success({ content: '生成功', id: 'upStatus', duration: 10 });
  }
};
// 模板选择分类数据
const handelTplType = async (value: any) => {
  if (value == 'cate' && (!tablenameList.value || tablenameList.value.length == 0)) {
    tablenameList.value = await get_tablelist({ id: formData.value.id });
  }
};
const handleIcon = (icon: any) => {
  formData.value.icon = icon;
};
</script>

<style lang="less" scoped>
@import '@/assets/style/formlayer.less';
.gcodebox {
  padding: 25px;
  .textbox {
    color: var(--color-neutral-10);
  }
}
.btnbox {
  text-align: center;
}
.tigmsg {
  margin-top: 35px;
}
</style>
