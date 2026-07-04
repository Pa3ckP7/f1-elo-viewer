import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DriversListView from '@/views/DriversListView.vue'
import DriverDetailView from '@/views/DriverDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'standings', component: HomeView },
    { path: '/drivers', name: 'drivers-list', component: DriversListView },
    { path: '/drivers/:driverRef', name: 'driver', component: DriverDetailView, props: true },
  ],
})

export default router
