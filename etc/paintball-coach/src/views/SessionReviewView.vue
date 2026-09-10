<script setup lang="ts">
import FieldCanvas from '@/components/FieldCanvas.vue'
import {
  allEvents,
  downloadSessionExport,
  exportPayload,
  playerName,
  pointSummaries,
  recommendations,
  state,
} from '@/stores/coachState'
</script>

<template>
  <section class="screen-grid">
    <div class="panel hero-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Session Review</p>
          <h1>Compare points, export the session, and capture coaching insight.</h1>
        </div>
        <div class="badge-group">
          <span class="badge">Layouts saved: {{ state.savedLayouts.length }}</span>
          <span class="badge">Notes parsed: {{ state.parsedNotes.length }}</span>
        </div>
      </div>
      <FieldCanvas :events="allEvents" mode="review" />
      <div class="button-row review-actions">
        <button class="primary" @click="downloadSessionExport">Export session JSON</button>
      </div>
      <textarea class="export-preview" :value="JSON.stringify(exportPayload, null, 2)" rows="12" readonly></textarea>
    </div>

    <aside class="stack">
      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Point comparison</p>
            <h2>What changed by point?</h2>
          </div>
        </div>
        <div class="summary-cards">
          <article v-for="summary in pointSummaries" :key="summary.id" class="summary-card">
            <header>
              <strong>{{ summary.name }}</strong>
              <span class="pill">{{ summary.outcome }}</span>
            </header>
            <p>{{ summary.side }} side · {{ summary.eventCount }} total tags</p>
            <ul>
              <li>{{ summary.movementEvents }} movement tags</li>
              <li>{{ summary.laneEvents }} lane tags</li>
              <li>{{ summary.eliminations }} eliminations</li>
              <li>{{ summary.notes }} coach notes</li>
            </ul>
          </article>
        </div>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Coaching insight</p>
            <h2>AI-style recommendations</h2>
          </div>
        </div>
        <ul class="insight-list">
          <li v-for="recommendation in recommendations" :key="recommendation">{{ recommendation }}</li>
        </ul>
        <div class="roadmap-box">
          <p class="mini-heading">AI integration hooks</p>
          <ul>
            <li>Computer vision handoff for player detection and zone occupancy.</li>
            <li>Transformer-ready note parsing from the live coach notebook.</li>
            <li>Post-match summaries that combine layouts, point outcomes, and heat clusters.</li>
          </ul>
        </div>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Parsed note review</p>
            <h2>Structured note context</h2>
          </div>
        </div>
        <ul class="event-list">
          <li v-for="note in state.parsedNotes.slice(0, 8)" :key="note.id">
            <strong>{{ note.suggestedEventType ?? 'note' }}</strong>
            <span>{{ note.text }}</span>
            <small>
              Players: {{ note.relatedPlayerIds.map(playerName).join(', ') || 'n/a' }} · Zones:
              {{ note.relatedZoneLabels.join(', ') || 'n/a' }}
            </small>
          </li>
        </ul>
      </div>
    </aside>
  </section>
</template>
