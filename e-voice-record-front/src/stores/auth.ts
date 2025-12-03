import {useRouter} from "vue-router";

interface User {
    userId?: string;
    username?: string;
    email?: string;
    token?: string;
    [key: string]: any; // 允许其他属性
}


export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null as User | null,
    }),
    actions: {
        login(user: User) {
            this.user = user;
        },
        logout() {
            const router = useRouter()
            this.user = null;
            router.push('/login')
        },
    },
    getters: {
        isAuthenticated: (state) => !!state.user,
        getUser: (state) => state.user,
    },
});