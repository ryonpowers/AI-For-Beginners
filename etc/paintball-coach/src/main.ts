import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { enablePersistence, hydrateState } from '@/stores/coachState'

hydrateState()
enablePersistence()

createApp(App).use(router).mount('#app')
