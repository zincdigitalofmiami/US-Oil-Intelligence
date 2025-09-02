import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import SecretsManagement from './views/Admin/SecretsManagement.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/admin/secrets',
    name: 'SecretsManagement',
    component: SecretsManagement
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
