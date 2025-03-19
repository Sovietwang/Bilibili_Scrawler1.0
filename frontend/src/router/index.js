import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/History.vue'
import Crawler from "@/views/Crawler.vue";
import History from "@/views/History.vue";
import Profile from "@/views/Profile.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/crawler", // 默认跳转到数据爬取页面
    },
    {
      path: "/crawler",
      name: "Crawler",
      component: Crawler,
    },
    {
      path: "/history",
      name: "History",
      component: History,
    },
    {
      path: "/profile",
      name: "Profile",
      component: Profile,
    },
    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue'),
    // },
  ],
})

export default router
