import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.VITE_BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { title: '登录', public: true }
    },
    {
      path: '/',
      name: 'MeetingList',
      component: () => import('@/views/MeetingList.vue'),
      meta: { title: '会议列表' }
    },
    {
      path: '/new',
      name: 'NewMeeting',
      component: () => import('@/views/NewMeeting.vue'),
      meta: { title: '新建会议' }
    },
    {
      path: '/detail/:id',
      name: 'MeetingDetail',
      component: () => import('@/views/MeetingDetail.vue'),
      meta: { title: '会议详情' }
    }
  ]
})

// 路由守卫 - 登录验证和页面标题
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - MDT会议纪要`
  }

  // 检查是否需要登录
  const token = localStorage.getItem('mdt_token')
  const isPublicPage = to.meta.public === true

  if (!isPublicPage && !token) {
    // 需要登录但没有 token，跳转登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.path === '/login' && token) {
    // 已登录但访问登录页，跳转首页
    next('/')
  } else {
    next()
  }
})

export default router
