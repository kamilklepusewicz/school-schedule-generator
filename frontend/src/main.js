// SECTION: Imports
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/base.css';

// SECTION: Application Bootstrap
createApp(App).use(router).mount('#app');
