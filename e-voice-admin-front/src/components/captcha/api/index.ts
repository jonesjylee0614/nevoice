import { defHttp } from '@/utils/http';

const Api = {
  captcha: '/user/get_Captcha',
  checkCaptcha: '/user/check_Captcha '
};

// 列表数据
export function getLoginCaptcha(params: any) {
  return defHttp.get({ url: Api.captcha, params }, { errorMessageMode: 'message' });
}
