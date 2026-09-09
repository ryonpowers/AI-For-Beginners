<script setup lang="ts">
import FieldCanvas from '@/components/FieldCanvas.vue'
import { allEvents, heatPoints, liveMetrics, playerName, state } from '@/stores/coachState'
import type { MatchEventType } from '@/types'

const filterTypes: MatchEventType[] = ['move', 'lane', 'snap', 'elimination', 'penalty', 'win']

const toggleFilter = (eventType: MatchEventType) => {
  const exists = state.heatmapFilters.eventTypes.includes(eventType)

  state.heatmapFilters.eventTypes = exists
    ? state.heatmapFilters.eventTypes.filter((value) => value !== eventType)
    : [...state.heatmapFilters.eventTypes, eventType]
}
</script>

<template>
  <section class="screen-grid">
    <div class="panel hero-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Heat Map View</p>
          <h1>See pressure, deaths, and movement patterns update from the same event stream.</h1>
        </div>
        <div class="badge-group">
          <span class="badge">Visible points: {{ liveMetrics.visibleHeatPoints }}</span>
          <span class="badge">Heat intensity: {{ liveMetrics.totalHeat }}</span>
        </div>
      </div>
      <FieldCanvas :events="allEvents" :heat-points="heatPoints" :selected-position="state.selectedFieldPosition" mode="heatmap" />
      <div class="stat-grid compact-grid">
        <div class="stat-card">
          <span>Wins</span>
          <strong>{{ liveMetrics.wins }}</strong>
        </div>
        <div class="stat-card">
          <span>Losses</span>
          <strong>{{ liveMetrics.losses }}</strong>
        </div>
        <div class="stat-card">
          <span>Tagged players</span>
          <strong>{{ new Set(heatPoints.map((point) => point.playerId)).size }}</strong>
        </div>
      </div>
    </div>

    <aside class="stack">
      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Filters</p>
            <h2>Recalculate on the fly</h2>
          </div>
        </div>
        <div class="checkbox-grid">
          <label v-for="eventType in filterTypes" :key="eventType" class="checkbox-pill">
            <input :checked="state.heatmapFilters.eventTypes.includes(eventType)" type="checkbox" @change="toggleFilter(eventType)" />
            <span>{{ eventType }}</span>
          </label>
        </div>
        <label class="field-label">
          Player filter
          <select v-model="state.heatmapFilters.playerId">
            <option value="all">All players</option>
            <option v-for="player in state.players" :key="player.id" :value="player.id">{{ player.name }}</option>
          </select>
        </label>
        <label class="field-label">
          Side filter
          <select v-model="state.heatmapFilters.side">
            <option value="all">Both sides</option>
            <option value="north">North</option>
            <option value="south">South</option>
          </select>
        </label>
        <label class="field-label">
          Point filter
          <select v-model="state.heatmapFilters.pointId">
            <option value="all">All points</option>
            <option v-for="point in state.points" :key="point.id" :value="point.id">{{ point.name }}</option>
          </select>
        </label>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Event feed</p>
            <h2>Heat map source data</h2>
          </div>
        </div>
        <ul class="event-list">
          <li v-for="event in [...allEvents].reverse().slice(0, 8)" :key="event.id">
            <strong>{{ event.type }}</strong>
            <span>{{ playerName(event.playerId) }} · {{ event.position.x }}, {{ event.position.y }}</span>
            <small>{{ event.details || 'Manual tag' }}</small>
          </li>
        </ul>
      </div>
    </aside>
  </section>
</template>
