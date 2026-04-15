import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/lessons',
    },
    {
      path: '/lessons',
      name: 'lessons',
      component: () => import('@/views/LessonsView.vue'),
    },
    {
      path: '/students',
      name: 'students',
      component: () => import('@/views/StudentsView.vue'),
    },
    {
      path: '/subjects',
      name: 'subjects',
      component: () => import('@/views/SubjectsView.vue'),
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('@/views/AnalyticsView.vue'),
    },
  ],
})

export default router
