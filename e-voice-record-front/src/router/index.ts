import {createRouter, createWebHashHistory,} from 'vue-router';

const {VITE_BASE_URL} = import.meta.env;


const router = createRouter({
    history: createWebHashHistory(VITE_BASE_URL),
    routes: [
        {
            path: '/',
            name: 'Home',
            component: () => import('../views/Home.vue')
        },
        {
            path: '/login',
            name: 'Login',
            component: () => import('../views/Login.vue')
        },
        {
            path: '/voice-list',
            name: 'VoiceList',
            component: () => import('../views/VoiceList.vue')
        },
        {
            path: '/voice-record/:id',
            name: 'VoiceRecord',
            component: () => import('../views/VoiceRecord.vue')
        }
    ]
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'

    if (to.path !== '/' && to.path !== '/login' && !isLoggedIn) {
        next('/login')
    } else {
        next()
    }
})

export default router