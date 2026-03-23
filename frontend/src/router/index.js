import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AdminDataView from '../views/AdminDataView.vue';
import StyleGuideView from '../views/StyleGuideView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/admin-data',
      name: 'admin-data',
      component: AdminDataView
    },
    {
      path: '/style-guide',
      name: 'style-guide',
      component: StyleGuideView
    }
  ]
});

export default router;
