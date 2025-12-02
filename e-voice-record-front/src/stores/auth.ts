import {useRouter} from "vue-router";

interface User {
    id: number;
    name: string;
    email: string;
    token: string;
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