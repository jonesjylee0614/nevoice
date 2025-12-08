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
    
    // 检查是否有 token 参数（用于声纹录制链接直接访问）
    const hasToken = to.query.token

    // 允许访问的白名单路径
    const whiteList = ['/', '/login']
    
    // 如果有 token 参数，允许直接访问（token 会在页面中验证）
    if (hasToken) {
        next()
    } else if (whiteList.includes(to.path) || isLoggedIn) {
        next()
    } else {
        next('/login')
    }
})

export default router