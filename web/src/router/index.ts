import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DriversListView from '@/views/DriversListView.vue'
import DriverDetailView from '@/views/DriverDetailView.vue'
import AboutView from '@/views/AboutView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(_to, _from, savedPosition) {
    // savedPosition is set on browser back/forward -- restore it there,
    // otherwise (e.g. clicking into a driver from a scrolled list) start at the top
    return savedPosition ?? { top: 0 }
  },
  routes: [
    { path: '/', name: 'standings', component: HomeView },
    { path: '/drivers', name: 'drivers-list', component: DriversListView },
    { path: '/drivers/:driverRef', name: 'driver', component: DriverDetailView, props: true },
    { path: '/about', name: 'about', component: AboutView },
  ],
})

export default router
