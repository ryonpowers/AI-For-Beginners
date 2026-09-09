<script setup lang="ts">
import FieldCanvas from '@/components/FieldCanvas.vue'
import {
  addFieldObject,
  loadLayout,
  removeSelectedObject,
  resetLayout,
  saveCurrentLayout,
  selectedObject,
  setSelectedObject,
  state,
  updateSelectedObject,
} from '@/stores/coachState'
import type { FieldObjectType } from '@/types'

const objectTypes: FieldObjectType[] = ['bunker', 'lane', 'zone', 'startBox', 'danger', 'note']
</script>

<template>
  <section class="screen-grid">
    <div class="panel hero-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Layout Designer</p>
          <h1>Build and edit paintball field plans in layered view.</h1>
        </div>
        <div class="badge-group">
          <span class="badge">Base map: {{ state.fieldTemplateName }}</span>
          <span class="badge">Objects: {{ state.fieldObjects.length }}</span>
        </div>
      </div>
      <FieldCanvas
        :interactive="true"
        :selected-object-id="state.selectedObjectId"
        @field-click="addFieldObject"
        @select-object="setSelectedObject"
      />
      <p class="helper-text">Click anywhere on the field to drop the currently selected object type, then tune its size, label, and position from the controls.</p>
    </div>

    <aside class="stack">
      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Tooling</p>
            <h2>Placement controls</h2>
          </div>
        </div>
        <label class="field-label">
          Object type
          <select v-model="state.activeObjectType">
            <option v-for="type in objectTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </label>
        <label class="field-label">
          Layout name
          <input v-model="state.currentLayoutName" type="text" placeholder="Weekend layout" />
        </label>
        <div class="button-row">
          <button class="primary" @click="saveCurrentLayout">Save layout</button>
          <button class="ghost" @click="resetLayout">Reset field</button>
        </div>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Object editor</p>
            <h2>{{ selectedObject?.label ?? 'Select an object' }}</h2>
          </div>
        </div>
        <template v-if="selectedObject">
          <label class="field-label">
            Label
            <input :value="selectedObject.label" type="text" @input="updateSelectedObject({ label: ($event.target as HTMLInputElement).value })" />
          </label>
          <div class="dual-inputs">
            <label class="field-label">
              X
              <input :value="selectedObject.x" type="number" min="0" max="100" step="1" @input="updateSelectedObject({ x: Number(($event.target as HTMLInputElement).value) })" />
            </label>
            <label class="field-label">
              Y
              <input :value="selectedObject.y" type="number" min="0" max="60" step="1" @input="updateSelectedObject({ y: Number(($event.target as HTMLInputElement).value) })" />
            </label>
          </div>
          <div class="dual-inputs">
            <label class="field-label">
              Width
              <input :value="selectedObject.width" type="number" min="2" max="100" step="1" @input="updateSelectedObject({ width: Number(($event.target as HTMLInputElement).value) })" />
            </label>
            <label class="field-label">
              Height
              <input :value="selectedObject.height" type="number" min="0" max="60" step="1" @input="updateSelectedObject({ height: Number(($event.target as HTMLInputElement).value) })" />
            </label>
          </div>
          <div class="dual-inputs">
            <label class="field-label">
              Rotation
              <input :value="selectedObject.rotation" type="number" min="-90" max="90" step="1" @input="updateSelectedObject({ rotation: Number(($event.target as HTMLInputElement).value) })" />
            </label>
            <label class="field-label">
              Opacity
              <input :value="selectedObject.opacity" type="number" min="0.1" max="1" step="0.05" @input="updateSelectedObject({ opacity: Number(($event.target as HTMLInputElement).value) })" />
            </label>
          </div>
          <label class="field-label">
            Color
            <input :value="selectedObject.color" type="color" @input="updateSelectedObject({ color: ($event.target as HTMLInputElement).value })" />
          </label>
          <div v-if="selectedObject.points?.length === 2" class="lane-editor">
            <p class="mini-heading">Lane endpoints</p>
            <div class="dual-inputs">
              <label class="field-label">
                Start X
                <input :value="selectedObject.points[0].x" type="number" min="0" max="100" step="1" @input="updateSelectedObject({ points: [{ ...selectedObject.points[0], x: Number(($event.target as HTMLInputElement).value) }, selectedObject.points[1]] })" />
              </label>
              <label class="field-label">
                Start Y
                <input :value="selectedObject.points[0].y" type="number" min="0" max="60" step="1" @input="updateSelectedObject({ points: [{ ...selectedObject.points[0], y: Number(($event.target as HTMLInputElement).value) }, selectedObject.points[1]] })" />
              </label>
            </div>
            <div class="dual-inputs">
              <label class="field-label">
                End X
                <input :value="selectedObject.points[1].x" type="number" min="0" max="100" step="1" @input="updateSelectedObject({ points: [selectedObject.points[0], { ...selectedObject.points[1], x: Number(($event.target as HTMLInputElement).value) }] })" />
              </label>
              <label class="field-label">
                End Y
                <input :value="selectedObject.points[1].y" type="number" min="0" max="60" step="1" @input="updateSelectedObject({ points: [selectedObject.points[0], { ...selectedObject.points[1], y: Number(($event.target as HTMLInputElement).value) }] })" />
              </label>
            </div>
          </div>
          <button class="danger" @click="removeSelectedObject">Remove object</button>
        </template>
      </div>

      <div class="panel">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Saved layouts</p>
            <h2>Load a prior plan</h2>
          </div>
        </div>
        <div class="saved-layouts">
          <button v-for="layout in state.savedLayouts" :key="layout.id" class="saved-layout" @click="loadLayout(layout.id)">
            <strong>{{ layout.name }}</strong>
            <span>{{ layout.objects.length }} objects · {{ new Date(layout.updatedAt).toLocaleString() }}</span>
          </button>
        </div>
      </div>
    </aside>
  </section>
</template>
