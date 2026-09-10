<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { liveMetrics, state } from '@/stores/coachState'

const route = useRoute()

const navigation = [
  { label: 'Layout Designer', to: '/layout' },
  { label: 'Match Board', to: '/match-board' },
  { label: 'Heat Map View', to: '/heat-map' },
  { label: 'Session Review', to: '/review' },
]
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Paintball Coach</p>
        <h1>Live tactical planning, tagging, and review.</h1>
      </div>
      <div class="topbar-meta">
        <span class="badge">{{ state.teamName }} vs {{ state.opponentName }}</span>
        <span class="badge">{{ liveMetrics.totalEvents }} tracked events</span>
      </div>
    </header>

    <nav class="nav-tabs" aria-label="Primary">
      <RouterLink v-for="item in navigation" :key="item.to" :to="item.to" class="nav-tab" :class="{ active: route.path === item.to }">
        {{ item.label }}
      </RouterLink>
    </nav>

    <main>
      <RouterView />
    </main>
  </div>
</template>
