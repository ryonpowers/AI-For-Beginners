import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/layout' },
    { path: '/layout', name: 'layout', component: () => import('@/views/LayoutDesignerView.vue') },
    { path: '/match-board', name: 'match-board', component: () => import('@/views/MatchBoardView.vue') },
    { path: '/heat-map', name: 'heat-map', component: () => import('@/views/HeatMapView.vue') },
    { path: '/review', name: 'review', component: () => import('@/views/SessionReviewView.vue') },
  ],
})

export default router
