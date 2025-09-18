// axios配置  可自行根据项目进行更改，只需更改该文件即可，其他文件可以不动
// The axios configuration can be changed according to the project, just change the file, other files can be left unchanged

import type { AxiosResponse } from 'axios';
import { clone } from 'lodash-es';
import type { RequestOptions, Result } from '/#/axios';
import md5 from 'md5';
import { Message, Modal } from '@arco-design/web-vue';
import useUserStore from '@/store/modules/user';
import { deepMerge, setObjToUrlParams } from '@/utils';
import { isString } from '@/utils/is';
import { getToken } from '@/utils/auth';
import { AxiosRetry } from '@/utils/http/axiosRetry';
import type { AxiosTransform, CreateAxiosOptions } from './axiosTransform';
import { VAxios } from './Axios';
import { checkStatus } from './checkStatus';
import { ContentTypeEnum, RequestEnum, ResultEnum } from './httpEnum';
import { formatRequestDate, joinTimestamp } from './helper';

// 开发环境通过 vite 代理转发到后端：/api → http://localhost:8108
// 生产环境可通过 VITE_API_HOST 指定完整后端地址
const devPrefix = '/api';
const apiHost = import.meta.env.VITE_API_HOST || (import.meta.env.DEV ? devPrefix : '');
type Recordable<T = any> = Record<string, T>;
/** @description: 数据处理，方便区分多种处理方式 */
const transform: AxiosTransform = {
  /** @description: 处理响应数据。如果数据不是预期格式，可直接抛出错误 */
  transformResponseHook: (res: AxiosResponse<Result>, options: RequestOptions) => {
    const { isTransformResponse, isReturnNativeResponse } = options;
    // 是否返回原生响应头 比如：需要获取响应头时使用该属性
    if (isReturnNativeResponse) {
      return res;
    }
    // 不进行任何处理，直接返回
    // 用于页面代码可能需要直接获取code，data，message这些信息时开启
    if (!isTransformResponse) {
      return res.data;
    }
    // 错误的时候返回

    const resdata = res.data;
    if (!resdata) {
      // return '[HTTP] Request has no return value';
      throw new Error('请求出错，请稍候重试1！');
    }
    //  这里 code，data，message为 后台统一的字段，需要在 types.ts内修改为项目自己的接口返回格式
    const { code, data, message, token } = resdata;
    const userStore = useUserStore();

    // 如果token即将过去则刷新token
    // 这里逻辑可以根据项目进行修改
    const hasSuccess = resdata && Reflect.has(resdata, 'code') && code === ResultEnum.SUCCESS;
    if (hasSuccess) {
      if (options.successMessageMode === 'modal') {
        Modal.error({ title: '提交提示', content: resdata.message });
      } else if (options.successMessageMode === 'message') {
        Message.success(resdata.message);
      }
      // 请求成功后更新token
      if (token) {
        userStore.setTokenArr(token);
      }
      return data;
    }
    // 在此处根据自己项目的实际情况对不同的code执行不同的操作
    // 如果不希望中断当前请求，请return数据，否则直接抛出异常即可
    let msg = '';
    switch (code) {
      case ResultEnum.TIMEOUT:
        options.errorMessageMode = 'message'; // 第一错误提示
        msg = '登录超时,请重新登录!';
        userStore.setTokenData(undefined);
        userStore.logout(true);
        break;
      default:
        if (message) {
          msg = message;
        }
    }
    if (options.errorMessageMode === 'modal') {
      Modal.error({ title: '错误提示', content: msg });
    } else if (options.errorMessageMode === 'message') {
      Message.error(msg);
    }
    throw new Error(msg || '请求出错，请稍候重试！');
  },

  // 请求之前处理config
  beforeRequestHook: (config, options) => {
    const { apiUrl, isRootUrl, joinPrefix, joinParamsToUrl, formatDate, joinTime = true, urlPrefix } = options;

    if (joinPrefix) {
      config.url = `${urlPrefix}${config.url}`;
    }

    if (isRootUrl && apiUrl && isString(apiUrl)) {
      config.url = `${apiUrl}${config.url}`;
    }
    const params = config.params || {};
    const data = config.data || false;
    formatDate && data && !isString(data) && formatRequestDate(data);
    if (config.method?.toUpperCase() === RequestEnum.GET) {
      if (!isString(params)) {
        // 给 get 请求加上时间戳参数，避免从缓存中拿数据。
        config.params = Object.assign(params || {}, joinTimestamp(joinTime, false));
      } else {
        // 兼容restful风格
        config.url = `${config.url + params}${joinTimestamp(joinTime, true)}`;
        config.params = undefined;
      }
    } else if (!isString(params)) {
      formatDate && formatRequestDate(params);
      if (
        Reflect.has(config, 'data') &&
        config.data &&
        (Object.keys(config.data).length > 0 || config.data instanceof FormData)
      ) {
        config.data = data;
        config.params = params;
      } else {
        // 非GET请求如果没有提供data，则将params视为data
        config.data = params;
        config.params = undefined;
      }
      if (joinParamsToUrl) {
        config.url = setObjToUrlParams(config.url as string, { ...config.params, ...config.data });
      }
    } else {
      // 兼容restful风格
      config.url += params;
      config.params = undefined;
    }
    return config;
  },

  /** @description: 请求拦截器处理 */
  requestInterceptors: (config, options) => {
    // 请求之前处理config
    const token = getToken();
    if (token && (config as Recordable)?.requestOptions?.withToken !== false) {
      // jwt token
      (config as Recordable).headers.Authorization = options.authenticationScheme
        ? `${options.authenticationScheme} ${token}`
        : token;
    }
    // 接口验证
    const timestamp: number = Date.parse(new Date().toString()) / 1000;
    (config as Recordable).headers['verify-time'] = timestamp as any;
    (config as Recordable).headers['verify-encrypt'] = md5(import.meta.env.VITE_ENCRYPT + timestamp) as any;
    return config;
  },

  /** @description: 响应拦截器处理 */
  responseInterceptors: (res: AxiosResponse<any>) => {
    return res;
  },

  /** @description: 响应错误处理 */
  responseInterceptorsCatch: (axiosInstance: AxiosResponse, error: any) => {
    const { response, code, message, config } = error || {};
    const errorMessageMode = config?.requestOptions?.errorMessageMode || 'none';
    const msg: string = response?.data?.message || (response?.data?.error?.message ?? '');
    const err: string = error?.toString?.() ?? '';
    let errMessage = '';

    try {
      if (code === 'ECONNABORTED' && message.includes('timeout')) {
        errMessage = '接口请求超时,请刷新页面重试!';
      }
      if (err?.includes('Network Error')) {
        errMessage = '网络异常，请检查您的网络连接是否正常!';
      }

      if (errMessage) {
        if (errorMessageMode === 'modal') {
          Modal.error({ title: '错误提示', content: errMessage });
        } else if (errorMessageMode === 'message') {
          Message.error(`${errMessage}1`);
        }
        return Promise.reject(error);
      }
    } catch (e) {
      throw new Error(e as unknown as string);
    }

    checkStatus(error?.response?.status, msg, errorMessageMode);

    // 添加自动重试机制 保险起见 只针对GET请求
    const retryRequest = new AxiosRetry();
    const { isOpenRetry } = config.requestOptions.retryRequest;
    config.method?.toUpperCase() === RequestEnum.GET && isOpenRetry && retryRequest.retry(axiosInstance as any, error);
    return Promise.reject(error);
  }
};

function createAxios(opt?: Partial<CreateAxiosOptions>) {
  return new VAxios(
    // 深度合并
    deepMerge(
      {
        authenticationScheme: '',
        timeout: 3600 * 1000, // 接口超时时间 默认1小时，防止上传接口超时
        // 基础接口地址
        // baseURL: globSetting.apiHost,

        headers: { 'Content-Type': ContentTypeEnum.JSON },
        // 如果是form-data格式
        // headers: { 'Content-Type': ContentTypeEnum.FORM_URLENCODED },
        // 数据处理方式
        transform: clone(transform),
        // 配置项，下面的选项都可以在独立的接口请求中覆盖
        requestOptions: {
          // 默认将prefix 添加到url
          joinPrefix: true,
          // 是否返回原生响应头 比如：需要获取响应头时使用该属性
          isReturnNativeResponse: false,
          // 需要对返回数据进行处理
          isTransformResponse: true,
          // 是否添加接口地址
          isRootUrl: true,
          // post请求的时候添加参数到url
          joinParamsToUrl: false,
          // 格式化提交参数时间
          formatDate: true,
          // 消息提示类型
          errorMessageMode: 'message',
          // 接口地址：开发态为 /api，经由 vite 代理；生产态由环境变量提供
          apiUrl: apiHost,
          // 接口前缀：保持空，由各 API 直接以后端相对路径书写
          urlPrefix: '',
          //  是否加入时间戳
          joinTime: true,
          // 忽略重复请求
          ignoreCancelToken: true,
          // 是否携带token
          withToken: true,
          retryRequest: {
            isOpenRetry: false,
            count: 5,
            waitTime: 100
          }
        }
      },
      opt || {}
    )
  );
}
export const defHttp = createAxios();
