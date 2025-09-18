<template>
  <ACard
    class="general-card"
    :title="$t('workplace.quick.operation')"
    :header-style="{ paddingBottom: '0' }"
    :body-style="{ padding: '24px 20px 0 20px' }"
    :loading="loading"
  >
    <template #extra>
      <ALink @click="isedit = !isedit">{{ isedit ? '完成' : '管理' }}</ALink>
    </template>
    <ARow :gutter="8">
      <ACol v-for="link in links" :key="link.name" :span="8" class="wrapper" @click="openAndEdit(link)">
        <APopconfirm content="您确定要删除吗?" position="tr" @ok="handleDel(link)">
          <div v-if="isedit && link.is_common == 0" class="del" @click.stop="() => {}">
            <icon-minus-circle-fill style="color: red" size="15" />
          </div>
        </APopconfirm>
        <div class="icon">
          <component :is="link.icon" />
        </div>
        <ATypographyParagraph class="text">
          {{ $t(link.name) }}
        </ATypographyParagraph>
      </ACol>
      <ACol v-if="isedit" :span="8" class="wrapper" @click="addEditQuick(null)">
        <div class="icon">
          <component :is="IconPlus" />
        </div>
        <ATypographyParagraph class="text">添加</ATypographyParagraph>
      </ACol>
    </ARow>
    <ADivider class="split-line" style="margin: 0" />
    <QuickForm @register="registerModal" @success="fetchData" />
  </ACard>
</template>

<script lang="ts" setup>
import { Message } from '@arco-design/web-vue';
import { IconPlus } from '@arco-design/web-vue/es/icon';
import type { QuickItem } from '@/api/dashboard/workplace';
import { delQuick, getQuick } from '@/api/dashboard/workplace';
import useLoading from '@/hooks/loading';
import { useModal } from '@/components/Modal';
import QuickForm from './QuickForm.vue';
// api
const router = useRouter();
const [registerModal, { openModal }] = useModal();
const { loading, setLoading } = useLoading(true);
onMounted(() => {
  setTimeout(() => {
    fetchData();
  }, 800);
});
const isedit = ref(false);
const links = ref<QuickItem[]>([]);
const fetchData = async () => {
  setLoading(true);
  try {
    links.value = await getQuick({});
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};
// 删除
const handleDel = async (item: any) => {
  const res = await delQuick({ id: item.id });
  if (res) {
    fetchData();
    Message.success({ content: '删除成功', id: 'upStatus', duration: 2000 });
  }
};
// 打开或者编辑
const openAndEdit = (item: any) => {
  if (isedit.value) {
    addEditQuick(item);
  } else {
    // 跳转
    // eslint-disable-next-line no-lonely-if
    if (item.type == 1) {
      // 外部
      window.open(item.path_url, '_blank');
    } else {
      // 内部链接
      router.push({ name: item.path_url });
    }
  }
};
// 编辑会计按钮
const addEditQuick = (item: any) => {
  if (!item) {
    // 新增
    openModal(true, {
      isUpdate: false,
      record: null
    });
  } else {
    // 编辑
    openModal(true, {
      isUpdate: true,
      record: item
    });
  }
};
</script>

<style scoped lang="less">
.wrapper {
  position: relative;
  .del {
    position: absolute;
    right: 15px;
    top: -10px;
  }
}
</style>
