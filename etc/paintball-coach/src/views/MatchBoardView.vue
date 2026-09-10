<script setup lang="ts">
import FieldCanvas from '@/components/FieldCanvas.vue'
import {
  addMatchEvent,
  addPoint,
  currentPoint,
  liveMetrics,
  parseCoachNote,
  playerName,
  setCurrentPoint,
  setSelectedFieldPosition,
  state,
  updateCurrentPoint,
} from '@/stores/coachState'
import type { MatchEventType, PointOutcome, PointSide } from '@/types'

const eventTypes: MatchEventType[] = ['move', 'lane', 'snap', 'elimination', 'penalty', 'win']
const pointSides: PointSide[] = ['north', 'south']
const pointOutcomes: PointOutcome[] = ['ongoing', 'win', 'loss', 'draw']
</script>

<template>
  <section class="screen-grid">
    <div class="panel hero-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Match Board</p>
          <h1>Tag each point live without leaving the field map.</h1>
        </div>
        <div class="badge-group">
          <span class="badge">{{ state.teamName }} vs {{ state.opponentName }}</span>
          <span class="badge">Point: {{ currentPoint?.name }}</span>
        </div>
      </div>
      <FieldCanvas
        :events="currentPoint?.events ?? []"
        :interactive="true"
        :selected-position="state.selectedFieldPosition"
        mode="events"
        @field-click="setSelectedFieldPosition"
      />
      <div class="stat-grid compact-grid">
        <div class="stat-card">
          <span>Total points</span>
          <strong>{{ liveMetrics.totalPoints }}</strong>
        </div>
        <div class="stat-card">
          <span>Total events</span>
          <strong>{{ liveMetrics.totalEvents }}</strong>
        </div>
        <div class="stat-card">
          <span>Current point tags</span>
          <strong>{{ currentPoint?.events.length ?? 0 }}</strong>
        </div>
      </div>
    </div>

    <aside class="stack">
      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Session setup</p>
            <h2>Roster and point context</h2>
          </div>
        </div>
        <div class="dual-inputs">
          <label class="field-label">
            Team
            <input v-model="state.teamName" type="text" />
          </label>
          <label class="field-label">
            Opponent
            <input v-model="state.opponentName" type="text" />
          </label>
        </div>
        <div class="dual-inputs">
          <label class="field-label">
            Active point
            <select :value="state.currentPointId" @change="setCurrentPoint(($event.target as HTMLSelectElement).value)">
              <option v-for="point in state.points" :key="point.id" :value="point.id">{{ point.name }}</option>
            </select>
          </label>
          <label class="field-label">
            Point name
            <input :value="currentPoint?.name" type="text" @input="updateCurrentPoint({ name: ($event.target as HTMLInputElement).value })" />
          </label>
        </div>
        <div class="dual-inputs">
          <label class="field-label">
            Side
            <select :value="currentPoint?.side" @change="updateCurrentPoint({ side: ($event.target as HTMLSelectElement).value as PointSide })">
              <option v-for="side in pointSides" :key="side" :value="side">{{ side }}</option>
            </select>
          </label>
          <label class="field-label">
            Outcome
            <select :value="currentPoint?.outcome" @change="updateCurrentPoint({ outcome: ($event.target as HTMLSelectElement).value as PointOutcome })">
              <option v-for="outcome in pointOutcomes" :key="outcome" :value="outcome">{{ outcome }}</option>
            </select>
          </label>
        </div>
        <button class="ghost" @click="addPoint">Add point</button>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Live tagger</p>
            <h2>Drop an event at the selected crosshair</h2>
          </div>
        </div>
        <div class="dual-inputs">
          <label class="field-label">
            Event type
            <select v-model="state.eventDraft.type">
              <option v-for="eventType in eventTypes" :key="eventType" :value="eventType">{{ eventType }}</option>
            </select>
          </label>
          <label class="field-label">
            Player
            <select v-model="state.eventDraft.playerId">
              <option v-for="player in state.players" :key="player.id" :value="player.id">{{ player.name }} · {{ player.role }}</option>
            </select>
          </label>
        </div>
        <div class="dual-inputs">
          <label class="field-label">
            Side
            <select v-model="state.eventDraft.side">
              <option v-for="side in pointSides" :key="side" :value="side">{{ side }}</option>
            </select>
          </label>
          <label class="field-label">
            Intensity
            <input v-model.number="state.eventDraft.intensity" type="range" min="1" max="5" />
            <span class="inline-help">{{ state.eventDraft.intensity }}/5</span>
          </label>
        </div>
        <label class="field-label">
          Details
          <textarea v-model="state.eventDraft.details" rows="3" placeholder="Breakout lane closed the snake wire"></textarea>
        </label>
        <div class="location-chip">Selected spot: {{ state.selectedFieldPosition.x }}, {{ state.selectedFieldPosition.y }}</div>
        <button class="primary" @click="addMatchEvent">Add event</button>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Coach notes</p>
            <h2>AI-ready note parsing</h2>
          </div>
        </div>
        <label class="field-label">
          Coach note
          <textarea v-model="state.coachNoteDraft" rows="4" placeholder="Alex won the snake breakout but the center got caught by cross-field pressure."></textarea>
        </label>
        <button class="ghost" @click="parseCoachNote">Parse note into tactical tags</button>
        <ul class="event-list parsed-list">
          <li v-for="note in state.parsedNotes.slice(0, 4)" :key="note.id">
            <strong>{{ note.suggestedEventType ?? 'note' }}</strong>
            <span>{{ note.text }}</span>
            <small>{{ note.tags.join(' · ') || 'manual review' }}</small>
          </li>
        </ul>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Timeline</p>
            <h2>Current point replay</h2>
          </div>
        </div>
        <ul class="event-list">
          <li v-for="event in [...(currentPoint?.events ?? [])].reverse()" :key="event.id">
            <strong>{{ event.type }}</strong>
            <span>{{ playerName(event.playerId) }} · {{ event.position.x }}, {{ event.position.y }}</span>
            <small>{{ event.details || 'No detail added' }}</small>
          </li>
        </ul>
      </div>
    </aside>
  </section>
</template>
