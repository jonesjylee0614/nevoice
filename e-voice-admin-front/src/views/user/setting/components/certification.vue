<template>
  <ASpin :loading="loading" style="width: 100%">
    <EnterpriseCertification :user-data="userData" />
    <CertificationRecords :render-data="userData" />
  </ASpin>
</template>

<script lang="ts" setup>
import { getCertification } from '@/api/user-center';
import useLoading from '@/hooks/loading';
import EnterpriseCertification from './enterprise-certification.vue';
import CertificationRecords from './certification-records.vue';

const { loading, setLoading } = useLoading(true);
const userData = ref();
const fetchData = async () => {
  try {
    userData.value = await getCertification();
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};
fetchData();
</script>

<style scoped lang="less"></style>
