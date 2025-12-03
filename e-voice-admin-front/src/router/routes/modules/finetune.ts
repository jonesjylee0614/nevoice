import type { AppRouteRecordRaw } from '@/router/types';

const routes: AppRouteRecordRaw[] = [
  {
    path: '/finetune',
    name: 'finetune',
    component: 'LAYOUT',
    meta: {
      locale: '模型微调',
      icon: 'icon-robot',
      requiresAuth: true,
      order: 30
    },
    children: [
      {
        path: 'task',
        name: 'finetuneTask',
        component: '/finetune/task/index',
        meta: {
          locale: '微调任务管理',
          requiresAuth: true
        }
      },
      {
        path: 'detail',
        name: 'finetuneDetail',
        component: '/finetune/detail/index',
        meta: {
          locale: '语料管理',
          requiresAuth: true
        }
      }
    ]
  }
];

export default routes;
