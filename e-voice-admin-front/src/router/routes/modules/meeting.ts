import type { AppRouteRecordRaw } from '@/router/types';

const routes: AppRouteRecordRaw[] = [
  {
    path: '/meeting',
    name: 'meeting',
    component: 'LAYOUT',
    meta: {
      locale: '会议管理',
      icon: 'icon-calendar',
      requiresAuth: true,
      order: 30
    },
    children: [
      {
        path: 'mdt',
        name: 'meetingMdt',
        component: '/meeting/mdt/index',
        meta: {
          locale: 'MDT会议',
          requiresAuth: true
        }
      },
      {
        path: 'mdt/detail',
        name: 'meetingMdtDetail',
        component: '/meeting/mdt/Detail',
        meta: {
          locale: '会议详情',
          requiresAuth: true,
          hideInMenu: true
        }
      },
      {
        path: 'offline',
        name: 'meetingOffline',
        component: '/meeting/offline/index',
        meta: {
          locale: '离线会议',
          requiresAuth: true
        }
      }
    ]
  }
];

export default routes;
