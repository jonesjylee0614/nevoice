import type { AppRouteRecordRaw } from '@/router/types';

const routes: AppRouteRecordRaw[] = [
  {
    path: '/home',
    name: 'home',
    component: '/dashboard/workplace/index',
    meta: {
      locale: '首页',
      requiresAuth: true,
      affix: true,
      icon: 'icon-home'
    }
  }
];

export default routes;
