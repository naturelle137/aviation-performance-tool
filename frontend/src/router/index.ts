import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('@/views/HomeView.vue'),
            meta: { title: 'Dashboard' }
        },
        {
            path: '/aircraft',
            name: 'aircraft',
            component: () => import('@/views/AircraftView.vue'),
            meta: { title: 'Aircraft' }
        },
        {
            path: '/aircraft/:id',
            name: 'aircraft-detail',
            component: () => import('@/views/AircraftDetailView.vue'),
            meta: { title: 'Aircraft Details' }
        },
        {
            path: '/calculation',
            name: 'calculation',
            component: () => import('@/views/CalculationView.vue'),
            meta: { title: 'New Calculation' }
        },
        {
            path: '/settings',
            name: 'settings',
            component: () => import('@/views/SettingsView.vue'),
            meta: { title: 'Settings' }
        }
    ]
})

// Update document title on navigation
router.beforeEach((to, _from, next) => {
    document.title = `${to.meta.title || 'Aviation'} | Aviation Performance Tool`
    next()
})

export default router
