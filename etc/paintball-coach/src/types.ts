export type ScreenRoute = 'layout' | 'match-board' | 'heat-map' | 'review'
export type FieldObjectType = 'bunker' | 'lane' | 'zone' | 'startBox' | 'note' | 'danger'
export type MatchEventType = 'move' | 'lane' | 'snap' | 'elimination' | 'penalty' | 'win'
export type PointSide = 'north' | 'south'
export type PointOutcome = 'win' | 'loss' | 'draw' | 'ongoing'

export interface Coordinate {
  x: number
  y: number
}

export interface FieldObject {
  id: string
  type: FieldObjectType
  label: string
  x: number
  y: number
  width: number
  height: number
  rotation: number
  color: string
  opacity: number
  points?: Coordinate[]
}

export interface Player {
  id: string
  name: string
  role: string
}

export interface MatchEvent {
  id: string
  type: MatchEventType
  playerId: string
  pointId: string
  side: PointSide
  position: Coordinate
  intensity: number
  details: string
  createdAt: string
}

export interface PointRecord {
  id: string
  name: string
  side: PointSide
  outcome: PointOutcome
  createdAt: string
  events: MatchEvent[]
  coachNotes: string[]
}

export interface SavedLayout {
  id: string
  name: string
  objects: FieldObject[]
  updatedAt: string
}

export interface ParsedNote {
  id: string
  pointId: string
  text: string
  tags: string[]
  suggestedEventType: MatchEventType | null
  relatedPlayerIds: string[]
  relatedZoneLabels: string[]
  createdAt: string
}

export interface HeatPoint extends Coordinate {
  id: string
  type: MatchEventType
  playerId: string
  pointId: string
  side: PointSide
  weight: number
}

export interface PointSummary {
  id: string
  name: string
  side: PointSide
  outcome: PointOutcome
  eventCount: number
  eliminations: number
  movementEvents: number
  laneEvents: number
  notes: number
}

export interface SessionExport {
  generatedAt: string
  teamName: string
  opponentName: string
  players: Player[]
  fieldObjects: FieldObject[]
  savedLayouts: SavedLayout[]
  points: PointRecord[]
  parsedNotes: ParsedNote[]
}
