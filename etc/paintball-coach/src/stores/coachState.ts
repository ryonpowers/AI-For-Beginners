import { computed, reactive, watch } from 'vue'
import type {
  Coordinate,
  FieldObject,
  FieldObjectType,
  HeatPoint,
  MatchEvent,
  MatchEventType,
  ParsedNote,
  Player,
  PointOutcome,
  PointRecord,
  PointSide,
  PointSummary,
  SavedLayout,
  SessionExport,
} from '@/types'

const STORAGE_KEY = 'paintball-coach-state-v1'
const FIELD_WIDTH = 100
const FIELD_HEIGHT = 60

const now = () => new Date().toISOString()
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value))
const createId = (prefix: string) => `${prefix}-${Math.random().toString(36).slice(2, 10)}`
const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value))

const baseFieldObjects: FieldObject[] = [
  { id: 'obj-home', type: 'startBox', label: 'Home Start', x: 10, y: 24, width: 10, height: 12, rotation: 0, color: '#38bdf8', opacity: 0.3 },
  { id: 'obj-away', type: 'startBox', label: 'Away Start', x: 80, y: 24, width: 10, height: 12, rotation: 0, color: '#f97316', opacity: 0.3 },
  { id: 'obj-snake', type: 'bunker', label: 'Snake Insert', x: 24, y: 8, width: 16, height: 8, rotation: -6, color: '#22c55e', opacity: 0.7 },
  { id: 'obj-dorito', type: 'zone', label: 'Dorito Lane', x: 58, y: 40, width: 18, height: 10, rotation: 10, color: '#a855f7', opacity: 0.22 },
  { id: 'obj-danger', type: 'danger', label: 'Cross-field Pressure', x: 42, y: 22, width: 16, height: 14, rotation: 0, color: '#ef4444', opacity: 0.18 },
  {
    id: 'obj-breakout',
    type: 'lane',
    label: 'Breakout Lane',
    x: 14,
    y: 26,
    width: 34,
    height: 0,
    rotation: 0,
    color: '#facc15',
    opacity: 0.9,
    points: [
      { x: 14, y: 26 },
      { x: 48, y: 18 },
    ],
  },
]

const players: Player[] = [
  { id: 'p1', name: 'Alex', role: 'Front snake' },
  { id: 'p2', name: 'Brooke', role: 'Front dorito' },
  { id: 'p3', name: 'Carter', role: 'Center attacker' },
  { id: 'p4', name: 'Drew', role: 'Back left' },
  { id: 'p5', name: 'Evan', role: 'Back right' },
]

const pointOneId = 'point-1'
const pointTwoId = 'point-2'

const basePoints: PointRecord[] = [
  {
    id: pointOneId,
    name: 'Point 1',
    side: 'north',
    outcome: 'win',
    createdAt: now(),
    coachNotes: ['Snake breakout won the wire early.'],
    events: [
      { id: createId('event'), type: 'move', playerId: 'p1', pointId: pointOneId, side: 'north', position: { x: 28, y: 12 }, intensity: 4, details: 'Snake insert off the break', createdAt: now() },
      { id: createId('event'), type: 'lane', playerId: 'p4', pointId: pointOneId, side: 'north', position: { x: 40, y: 20 }, intensity: 5, details: 'Heavy lane through the center', createdAt: now() },
      { id: createId('event'), type: 'elimination', playerId: 'p2', pointId: pointOneId, side: 'north', position: { x: 67, y: 42 }, intensity: 5, details: 'Closed the dorito corner', createdAt: now() },
    ],
  },
  {
    id: pointTwoId,
    name: 'Point 2',
    side: 'south',
    outcome: 'loss',
    createdAt: now(),
    coachNotes: ['Cross-field pressure caught the center move.'],
    events: [
      { id: createId('event'), type: 'move', playerId: 'p3', pointId: pointTwoId, side: 'south', position: { x: 46, y: 28 }, intensity: 3, details: 'Center fill after breakout', createdAt: now() },
      { id: createId('event'), type: 'elimination', playerId: 'p3', pointId: pointTwoId, side: 'south', position: { x: 51, y: 25 }, intensity: 5, details: 'Cross-field shot on the center', createdAt: now() },
      { id: createId('event'), type: 'lane', playerId: 'p5', pointId: pointTwoId, side: 'south', position: { x: 58, y: 18 }, intensity: 4, details: 'Back-right laning the snake wire', createdAt: now() },
    ],
  },
]

const defaultLayout: SavedLayout = {
  id: 'layout-default',
  name: 'Standard XBall',
  objects: clone(baseFieldObjects),
  updatedAt: now(),
}

interface CoachState {
  teamName: string
  opponentName: string
  fieldTemplateName: string
  currentLayoutName: string
  fieldObjects: FieldObject[]
  savedLayouts: SavedLayout[]
  selectedObjectId: string | null
  activeObjectType: FieldObjectType
  players: Player[]
  points: PointRecord[]
  currentPointId: string
  eventDraft: {
    type: MatchEventType
    playerId: string
    side: PointSide
    intensity: number
    details: string
  }
  selectedFieldPosition: Coordinate
  coachNoteDraft: string
  parsedNotes: ParsedNote[]
  heatmapFilters: {
    eventTypes: MatchEventType[]
    playerId: string
    side: PointSide | 'all'
    pointId: string
  }
}

export const state = reactive<CoachState>({
  teamName: 'Raiders',
  opponentName: 'Spartans',
  fieldTemplateName: 'Tournament Airball',
  currentLayoutName: 'Standard XBall',
  fieldObjects: clone(baseFieldObjects),
  savedLayouts: [defaultLayout],
  selectedObjectId: 'obj-snake',
  activeObjectType: 'bunker',
  players: clone(players),
  points: clone(basePoints),
  currentPointId: pointOneId,
  eventDraft: {
    type: 'move',
    playerId: 'p1',
    side: 'north',
    intensity: 4,
    details: '',
  },
  selectedFieldPosition: { x: 50, y: 30 },
  coachNoteDraft: '',
  parsedNotes: [],
  heatmapFilters: {
    eventTypes: ['move', 'lane', 'elimination'],
    playerId: 'all',
    side: 'all',
    pointId: 'all',
  },
})

let persistenceEnabled = false

const getObjectCenter = (object: FieldObject) => {
  const start = object.points?.[0]
  const end = object.points?.[1]

  if (start && end) {
    return { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 }
  }

  return { x: object.x + object.width / 2, y: object.y + object.height / 2 }
}

const nearestZoneLabel = (position: Coordinate) => {
  const nearest = state.fieldObjects.reduce(
    (best, object) => {
      const center = getObjectCenter(object)
      const distance = Math.hypot(center.x - position.x, center.y - position.y)
      return distance < best.distance ? { label: object.label, distance } : best
    },
    { label: 'Open field', distance: Number.POSITIVE_INFINITY },
  )

  return nearest.distance <= 14 ? nearest.label : 'Open field'
}

export const currentPoint = computed<PointRecord | undefined>(() => {
  return state.points.find((point) => point.id === state.currentPointId) ?? state.points[0]
})

export const allEvents = computed(() => {
  return state.points.flatMap((point) => point.events)
})

export const heatPoints = computed<HeatPoint[]>(() => {
  return allEvents.value
    .filter((event) => state.heatmapFilters.eventTypes.includes(event.type))
    .filter((event) => state.heatmapFilters.playerId === 'all' || event.playerId === state.heatmapFilters.playerId)
    .filter((event) => state.heatmapFilters.side === 'all' || event.side === state.heatmapFilters.side)
    .filter((event) => state.heatmapFilters.pointId === 'all' || event.pointId === state.heatmapFilters.pointId)
    .map((event) => ({
      id: event.id,
      x: event.position.x,
      y: event.position.y,
      type: event.type,
      playerId: event.playerId,
      pointId: event.pointId,
      side: event.side,
      weight: event.intensity,
    }))
})

export const pointSummaries = computed<PointSummary[]>(() => {
  return state.points.map((point) => ({
    id: point.id,
    name: point.name,
    side: point.side,
    outcome: point.outcome,
    eventCount: point.events.length,
    eliminations: point.events.filter((event) => event.type === 'elimination').length,
    movementEvents: point.events.filter((event) => event.type === 'move').length,
    laneEvents: point.events.filter((event) => event.type === 'lane').length,
    notes: point.coachNotes.length,
  }))
})

export const liveMetrics = computed(() => {
  const filteredPoints = state.heatmapFilters.pointId === 'all'
    ? state.points
    : state.points.filter((point) => point.id === state.heatmapFilters.pointId)

  const wins = filteredPoints.filter((point) => point.outcome === 'win').length
  const losses = filteredPoints.filter((point) => point.outcome === 'loss').length
  const totalHeat = heatPoints.value.reduce((sum, point) => sum + point.weight, 0)

  return {
    activeLayoutObjects: state.fieldObjects.length,
    totalPoints: state.points.length,
    totalEvents: allEvents.value.length,
    visibleHeatPoints: heatPoints.value.length,
    totalHeat,
    wins,
    losses,
  }
})

export const recommendations = computed(() => {
  const eliminationEvents = allEvents.value.filter((event) => event.type === 'elimination')
  const laneEvents = allEvents.value.filter((event) => event.type === 'lane')
  const moveEvents = allEvents.value.filter((event) => event.type === 'move')

  const countByZone = (events: MatchEvent[]) => {
    const zoneCounts = new Map<string, number>()

    events.forEach((event) => {
      const label = nearestZoneLabel(event.position)
      zoneCounts.set(label, (zoneCounts.get(label) ?? 0) + 1)
    })

    return [...zoneCounts.entries()].sort((left, right) => right[1] - left[1])
  }

  const topDangerZone = countByZone(eliminationEvents)[0]
  const strongestLane = countByZone(laneEvents)[0]
  const strongestMove = countByZone(moveEvents)[0]

  return [
    topDangerZone
      ? `Weak side alert: ${topDangerZone[0]} has produced ${topDangerZone[1]} elimination event(s).`
      : 'Weak side alert: record elimination events to expose recurring death zones.',
    strongestLane
      ? `Pressure trend: ${strongestLane[0]} is your hottest lane with ${strongestLane[1]} lane tag(s).`
      : 'Pressure trend: add lane events on the board to surface lane density.',
    strongestMove
      ? `Breakout read: ${strongestMove[0]} is your busiest movement lane with ${strongestMove[1]} move tag(s).`
      : 'Breakout read: tag movement paths to compare successful breakout routes.',
  ]
})

export const exportPayload = computed<SessionExport>(() => ({
  generatedAt: now(),
  teamName: state.teamName,
  opponentName: state.opponentName,
  players: clone(state.players),
  fieldObjects: clone(state.fieldObjects),
  savedLayouts: clone(state.savedLayouts),
  points: clone(state.points),
  parsedNotes: clone(state.parsedNotes),
}))

export const selectedObject = computed(() => {
  return state.fieldObjects.find((object) => object.id === state.selectedObjectId) ?? null
})

export const setSelectedFieldPosition = (position: Coordinate) => {
  state.selectedFieldPosition = {
    x: clamp(Number(position.x.toFixed(2)), 0, FIELD_WIDTH),
    y: clamp(Number(position.y.toFixed(2)), 0, FIELD_HEIGHT),
  }
}

export const setSelectedObject = (objectId: string | null) => {
  state.selectedObjectId = objectId
}

export const addFieldObject = (position: Coordinate) => {
  const x = clamp(position.x, 0, FIELD_WIDTH)
  const y = clamp(position.y, 0, FIELD_HEIGHT)
  const baseObject: FieldObject = {
    id: createId('obj'),
    type: state.activeObjectType,
    label: `${state.activeObjectType} ${state.fieldObjects.filter((object) => object.type === state.activeObjectType).length + 1}`,
    x: clamp(x - 6, 0, FIELD_WIDTH - 12),
    y: clamp(y - 4, 0, FIELD_HEIGHT - 8),
    width: state.activeObjectType === 'lane' ? 18 : 12,
    height: state.activeObjectType === 'lane' ? 0 : 8,
    rotation: 0,
    color:
      state.activeObjectType === 'danger'
        ? '#ef4444'
        : state.activeObjectType === 'zone'
          ? '#a855f7'
          : state.activeObjectType === 'startBox'
            ? '#0ea5e9'
            : state.activeObjectType === 'note'
              ? '#f97316'
              : '#22c55e',
    opacity: state.activeObjectType === 'lane' ? 0.95 : 0.32,
  }

  if (state.activeObjectType === 'lane') {
    baseObject.points = [
      { x: clamp(x - 8, 0, FIELD_WIDTH), y },
      { x: clamp(x + 10, 0, FIELD_WIDTH), y: clamp(y - 6, 0, FIELD_HEIGHT) },
    ]
  }

  state.fieldObjects.push(baseObject)
  state.selectedObjectId = baseObject.id
}

export const updateSelectedObject = (patch: Partial<FieldObject>) => {
  const object = selectedObject.value
  if (!object) return

  Object.assign(object, patch)

  object.x = clamp(object.x, 0, FIELD_WIDTH)
  object.y = clamp(object.y, 0, FIELD_HEIGHT)
  object.width = clamp(object.width, 2, FIELD_WIDTH)
  object.height = clamp(object.height, 0, FIELD_HEIGHT)
  object.opacity = clamp(object.opacity, 0.05, 1)

  if (object.points?.length === 2) {
    object.points = object.points.map((point) => ({
      x: clamp(point.x, 0, FIELD_WIDTH),
      y: clamp(point.y, 0, FIELD_HEIGHT),
    }))
  }
}

export const removeSelectedObject = () => {
  if (!state.selectedObjectId) return

  state.fieldObjects = state.fieldObjects.filter((object) => object.id !== state.selectedObjectId)
  state.selectedObjectId = state.fieldObjects[0]?.id ?? null
}

export const saveCurrentLayout = () => {
  const layoutName = state.currentLayoutName.trim() || `Layout ${state.savedLayouts.length + 1}`
  const existing = state.savedLayouts.find((layout) => layout.name === layoutName)
  const payload: SavedLayout = {
    id: existing?.id ?? createId('layout'),
    name: layoutName,
    objects: clone(state.fieldObjects),
    updatedAt: now(),
  }

  if (existing) {
    state.savedLayouts = state.savedLayouts.map((layout) => (layout.id === existing.id ? payload : layout))
  } else {
    state.savedLayouts.unshift(payload)
  }
}

export const loadLayout = (layoutId: string) => {
  const layout = state.savedLayouts.find((item) => item.id === layoutId)
  if (!layout) return

  state.currentLayoutName = layout.name
  state.fieldObjects = clone(layout.objects)
  state.selectedObjectId = state.fieldObjects[0]?.id ?? null
}

export const resetLayout = () => {
  state.currentLayoutName = 'Standard XBall'
  state.fieldObjects = clone(baseFieldObjects)
  state.selectedObjectId = state.fieldObjects[0]?.id ?? null
}

export const addPoint = () => {
  const pointNumber = state.points.length + 1
  const nextPoint: PointRecord = {
    id: createId('point'),
    name: `Point ${pointNumber}`,
    side: state.eventDraft.side,
    outcome: 'ongoing',
    createdAt: now(),
    events: [],
    coachNotes: [],
  }

  state.points.push(nextPoint)
  state.currentPointId = nextPoint.id
}

export const setCurrentPoint = (pointId: string) => {
  state.currentPointId = pointId
}

export const updateCurrentPoint = (patch: Partial<Pick<PointRecord, 'name' | 'side' | 'outcome'>>) => {
  if (!currentPoint.value) return
  Object.assign(currentPoint.value, patch)
}

export const addMatchEvent = () => {
  if (!currentPoint.value) return

  const matchEvent: MatchEvent = {
    id: createId('event'),
    type: state.eventDraft.type,
    playerId: state.eventDraft.playerId,
    pointId: currentPoint.value.id,
    side: state.eventDraft.side,
    position: clone(state.selectedFieldPosition),
    intensity: state.eventDraft.intensity,
    details: state.eventDraft.details.trim(),
    createdAt: now(),
  }

  currentPoint.value.events.push(matchEvent)
  state.eventDraft.details = ''
}

export const parseCoachNote = () => {
  const note = state.coachNoteDraft.trim()
  if (!note || !currentPoint.value) return

  const normalized = note.toLowerCase()
  const suggestedEventType: MatchEventType | null = normalized.includes('lane')
    ? 'lane'
    : normalized.includes('snap')
      ? 'snap'
      : normalized.includes('penalty')
        ? 'penalty'
        : normalized.includes('elim') || normalized.includes('picked') || normalized.includes('caught')
          ? 'elimination'
          : normalized.includes('move') || normalized.includes('fill') || normalized.includes('bump')
            ? 'move'
            : normalized.includes('won')
              ? 'win'
              : null

  const relatedPlayerIds = state.players
    .filter((player) => normalized.includes(player.name.toLowerCase()))
    .map((player) => player.id)

  const relatedZoneLabels = state.fieldObjects
    .filter((object) => normalized.includes(object.label.toLowerCase().split(' ')[0] ?? ''))
    .map((object) => object.label)

  const tags = [
    ...(suggestedEventType ? [suggestedEventType] : []),
    ...relatedZoneLabels,
    ...(normalized.includes('weak') ? ['weak-side'] : []),
    ...(normalized.includes('breakout') ? ['breakout'] : []),
  ]

  currentPoint.value.coachNotes.push(note)
  state.parsedNotes.unshift({
    id: createId('note'),
    pointId: currentPoint.value.id,
    text: note,
    tags,
    suggestedEventType,
    relatedPlayerIds,
    relatedZoneLabels,
    createdAt: now(),
  })

  state.coachNoteDraft = ''
}

export const downloadSessionExport = () => {
  if (typeof window === 'undefined') return

  const blob = new Blob([JSON.stringify(exportPayload.value, null, 2)], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `paintball-session-${new Date().toISOString().slice(0, 10)}.json`
  link.click()
  window.URL.revokeObjectURL(url)
}

export const hydrateState = () => {
  if (typeof window === 'undefined') return

  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (!stored) return

  try {
    const parsed = JSON.parse(stored) as Partial<CoachState>

    if (parsed.teamName) state.teamName = parsed.teamName
    if (parsed.opponentName) state.opponentName = parsed.opponentName
    if (parsed.fieldTemplateName) state.fieldTemplateName = parsed.fieldTemplateName
    if (parsed.currentLayoutName) state.currentLayoutName = parsed.currentLayoutName
    if (Array.isArray(parsed.fieldObjects)) state.fieldObjects = parsed.fieldObjects
    if (Array.isArray(parsed.savedLayouts) && parsed.savedLayouts.length) state.savedLayouts = parsed.savedLayouts
    if (parsed.selectedObjectId !== undefined) state.selectedObjectId = parsed.selectedObjectId
    if (Array.isArray(parsed.players) && parsed.players.length) state.players = parsed.players
    if (Array.isArray(parsed.points) && parsed.points.length) state.points = parsed.points
    if (parsed.currentPointId) state.currentPointId = parsed.currentPointId
    if (parsed.eventDraft) Object.assign(state.eventDraft, parsed.eventDraft)
    if (parsed.selectedFieldPosition) state.selectedFieldPosition = parsed.selectedFieldPosition
    if (Array.isArray(parsed.parsedNotes)) state.parsedNotes = parsed.parsedNotes
    if (parsed.heatmapFilters) Object.assign(state.heatmapFilters, parsed.heatmapFilters)
  } catch (error) {
    console.error('Unable to hydrate paintball coach state', error)
  }
}

export const enablePersistence = () => {
  if (typeof window === 'undefined' || persistenceEnabled) return

  watch(
    state,
    (value) => {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          teamName: value.teamName,
          opponentName: value.opponentName,
          fieldTemplateName: value.fieldTemplateName,
          currentLayoutName: value.currentLayoutName,
          fieldObjects: value.fieldObjects,
          savedLayouts: value.savedLayouts,
          selectedObjectId: value.selectedObjectId,
          players: value.players,
          points: value.points,
          currentPointId: value.currentPointId,
          eventDraft: value.eventDraft,
          selectedFieldPosition: value.selectedFieldPosition,
          parsedNotes: value.parsedNotes,
          heatmapFilters: value.heatmapFilters,
        }),
      )
    },
    { deep: true },
  )

  persistenceEnabled = true
}

export const playerName = (playerId: string) => {
  return state.players.find((player) => player.id === playerId)?.name ?? 'Unknown player'
}

export const eventTypeColor = (eventType: MatchEventType) => {
  switch (eventType) {
    case 'move':
      return '#38bdf8'
    case 'lane':
      return '#f97316'
    case 'snap':
      return '#facc15'
    case 'elimination':
      return '#ef4444'
    case 'penalty':
      return '#a855f7'
    case 'win':
      return '#22c55e'
    default:
      return '#94a3b8'
  }
}
