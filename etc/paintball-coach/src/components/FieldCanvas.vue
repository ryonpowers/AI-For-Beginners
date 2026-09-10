<script setup lang="ts">
import { computed } from 'vue'
import { eventTypeColor, state } from '@/stores/coachState'
import type { Coordinate, FieldObject, HeatPoint, MatchEvent } from '@/types'

const props = withDefaults(
  defineProps<{
    events?: MatchEvent[]
    heatPoints?: HeatPoint[]
    interactive?: boolean
    mode?: 'design' | 'events' | 'heatmap' | 'review'
    selectedObjectId?: string | null
    selectedPosition?: Coordinate | null
  }>(),
  {
    events: () => [],
    heatPoints: () => [],
    interactive: false,
    mode: 'design',
    selectedObjectId: null,
    selectedPosition: null,
  },
)

const emit = defineEmits<{
  (event: 'field-click', position: Coordinate): void
  (event: 'select-object', objectId: string): void
}>()

const baseRows = computed(() => Array.from({ length: 6 }, (_, index) => index * 10))
const baseColumns = computed(() => Array.from({ length: 11 }, (_, index) => index * 10))

const objectCenter = (object: FieldObject) => {
  const start = object.points?.[0]
  const end = object.points?.[1]

  if (start && end) {
    return {
      x: (start.x + end.x) / 2,
      y: (start.y + end.y) / 2,
    }
  }

  return { x: object.x + object.width / 2, y: object.y + object.height / 2 }
}

const linePoint = (object: FieldObject, index: 0 | 1) => {
  return object.points?.[index] ?? { x: object.x, y: object.y }
}

const handleFieldClick = (event: MouseEvent) => {
  if (!props.interactive) return

  const svg = event.currentTarget as SVGSVGElement
  const rect = svg.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 100
  const y = ((event.clientY - rect.top) / rect.height) * 60
  emit('field-click', {
    x: Number(x.toFixed(2)),
    y: Number(y.toFixed(2)),
  })
}
</script>

<template>
  <div class="field-shell">
    <svg class="field-canvas" viewBox="0 0 100 60" @click="handleFieldClick">
      <defs>
        <radialGradient id="heat-bloom" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#f97316" stop-opacity="0.85" />
          <stop offset="65%" stop-color="#ef4444" stop-opacity="0.32" />
          <stop offset="100%" stop-color="#ef4444" stop-opacity="0" />
        </radialGradient>
      </defs>

      <rect x="1" y="1" width="98" height="58" rx="3" class="field-boundary" />
      <rect x="2.5" y="2.5" width="95" height="55" rx="2" class="field-play-surface" />
      <line x1="50" y1="2.5" x2="50" y2="57.5" class="field-midline" />
      <line x1="2.5" y1="30" x2="97.5" y2="30" class="field-crossline" />

      <g class="grid-layer">
        <line v-for="row in baseRows" :key="`row-${row}`" x1="2.5" :y1="row" x2="97.5" :y2="row" class="grid-line" />
        <line v-for="column in baseColumns" :key="`column-${column}`" :x1="column" y1="2.5" :x2="column" y2="57.5" class="grid-line" />
      </g>

      <g v-if="props.heatPoints.length" class="heat-layer">
        <circle
          v-for="point in props.heatPoints"
          :key="`heat-${point.id}`"
          :cx="point.x"
          :cy="point.y"
          :r="4 + point.weight * 2.2"
          fill="url(#heat-bloom)"
          :opacity="Math.min(0.18 + point.weight * 0.08, 0.82)"
        />
      </g>

      <g class="object-layer">
        <template v-for="object in state.fieldObjects" :key="object.id">
          <line
            v-if="object.type === 'lane' && object.points"
            :x1="linePoint(object, 0).x"
            :y1="linePoint(object, 0).y"
            :x2="linePoint(object, 1).x"
            :y2="linePoint(object, 1).y"
            :stroke="object.color"
            stroke-width="1.6"
            stroke-linecap="round"
            :stroke-opacity="object.opacity"
            @click.stop="emit('select-object', object.id)"
          />
          <g v-else @click.stop="emit('select-object', object.id)">
            <rect
              :x="object.x"
              :y="object.y"
              :width="object.width"
              :height="object.height"
              :fill="object.color"
              :fill-opacity="object.opacity"
              :stroke="selectedObjectId === object.id ? '#f8fafc' : object.color"
              :stroke-width="selectedObjectId === object.id ? 0.7 : 0.35"
              :transform="`rotate(${object.rotation} ${object.x + object.width / 2} ${object.y + object.height / 2})`"
              rx="1.6"
            />
          </g>
          <text
            :x="objectCenter(object).x"
            :y="objectCenter(object).y - 1.5"
            class="object-label"
            text-anchor="middle"
          >
            {{ object.label }}
          </text>
        </template>
      </g>

      <g v-if="props.events.length" class="event-layer">
        <g v-for="event in props.events" :key="event.id">
          <circle
            :cx="event.position.x"
            :cy="event.position.y"
            :r="1.2 + event.intensity * 0.55"
            :fill="eventTypeColor(event.type)"
            fill-opacity="0.94"
            stroke="#020617"
            stroke-width="0.4"
          />
          <text :x="event.position.x + 1.5" :y="event.position.y - 1.5" class="event-label">
            {{ event.type }}
          </text>
        </g>
      </g>

      <g v-if="props.selectedPosition" class="cursor-layer">
        <circle :cx="props.selectedPosition.x" :cy="props.selectedPosition.y" r="2.2" class="cursor-ring" />
        <line :x1="props.selectedPosition.x - 2.5" :y1="props.selectedPosition.y" :x2="props.selectedPosition.x + 2.5" :y2="props.selectedPosition.y" class="cursor-line" />
        <line :x1="props.selectedPosition.x" :y1="props.selectedPosition.y - 2.5" :x2="props.selectedPosition.x" :y2="props.selectedPosition.y + 2.5" class="cursor-line" />
      </g>
    </svg>
    <div class="field-legend">
      <span><i class="legend-swatch move"></i> Movement</span>
      <span><i class="legend-swatch lane"></i> Lane pressure</span>
      <span><i class="legend-swatch elimination"></i> Eliminations</span>
      <span><i class="legend-swatch danger"></i> Tactical objects</span>
    </div>
  </div>
</template>
