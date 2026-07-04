import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DriverView from '@/views/DriverView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'standings', component: HomeView },
    { path: '/drivers/:driverRef?', name: 'driver', component: DriverView, props: true },
  ],
})

export default router
