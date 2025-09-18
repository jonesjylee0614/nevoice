import { defHttp } from '@/utils/http';
const Api = {
  requirement: '/developer/codestore/requirement'
};

// 发布需求数据
export function requirement(params: any, baseurl: string) {
  return defHttp.post({ url: `${Api.requirement}?baseurl=${baseurl}`, params }, { errorMessageMode: 'message' });
}
