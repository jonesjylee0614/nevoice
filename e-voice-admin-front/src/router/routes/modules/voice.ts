import type { AppRouteRecordRaw } from '@/router/types';

const routes: AppRouteRecordRaw[] = [
  {
    path: '/voice',
    name: 'voice',
    component: 'LAYOUT',
    meta: {
      locale: '语音能力',
      icon: 'icon-sound',
      requiresAuth: true,
      order: 20
    },
    children: [
      {
        path: 'identify',
        name: 'voiceIdentify',
        component: '/voice/identify/index',
        meta: {
          locale: '实时语音识别',
          requiresAuth: true
        }
      },
      {
        path: 'identify/online',
        name: 'voiceIdentifyOnline',
        component: '/voice/identify/online',
        meta: {
          locale: '在线语音识别',
          requiresAuth: true
        }
      },
      {
        path: 'identify/offline',
        name: 'voiceIdentifyOffline',
        component: '/voice/identify/offline',
        meta: {
          locale: '离线语音识别',
          requiresAuth: true
        }
      },
      {
        path: 'print',
        name: 'voicePrint',
        component: '/voice/print/index',
        meta: {
          locale: '声纹注册',
          requiresAuth: true
        }
      },
      {
        path: 'document',
        name: 'voiceDocument',
        component: '/voice/document/index',
        meta: {
          locale: '语料管理',
          requiresAuth: true
        }
      }
    ]
  }
];

export default routes;


