// SECTION: Imports
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AdminDataView from '../views/AdminDataView.vue';
import AdminDataWizardView from '../views/AdminDataWizardView.vue';
import StyleGuideView from '../views/StyleGuideView.vue';
import TimetableGenerationView from '../views/TimetableGenerationView.vue';
import TimetableManagementView from '../views/TimetableManagementView.vue';

// SECTION: Route Definitions
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
      path: '/admin-data-wizard',
      name: 'admin-data-wizard',
      component: AdminDataWizardView
    },
    {
      path: '/timetable-generation',
      name: 'timetable-generation',
      component: TimetableGenerationView
    },
    {
      path: '/timetable-management',
      name: 'timetable-management',
      component: TimetableManagementView
    },
    {
      path: '/style-guide',
      name: 'style-guide',
      component: StyleGuideView
    }
  ]
});

// SECTION: Router Export
export default router;
