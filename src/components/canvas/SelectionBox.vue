<template>
  <div v-if="bounds" class="selection-box" :style="boxStyle">
    <!-- Resize handles — each has pointer-events: all via CSS -->
    <div
      v-for="h in handles"
      :key="h.key"
      class="resize-handle"
      :class="`handle-${h.key}`"
      :style="h.style"
      @mousedown.stop.prevent="onHandleMousedown($event, h.key)"
    ></div>
    <!-- Dimension tooltip -->
    <div class="dimension-tip" v-if="showDim">{{ Math.round(bounds.w) }} × {{ Math.round(bounds.h) }}</div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { saveHistory } from '../../store/editorStore.js'

const props = defineProps({ selectedIds: Array, elements: Array, zoom: Number })
const emit = defineEmits(['resize', 'move'])

const showDim = ref(false)

const bounds = computed(() => {
  const els = props.elements.filter(e => props.selectedIds.includes(e.id))
  if (!els.length) return null
  const minX = Math.min(...els.map(e => e.x))
  const minY = Math.min(...els.map(e => e.y))
  const maxX = Math.max(...els.map(e => e.x + e.width))
  const maxY = Math.max(...els.map(e => e.y + e.height))
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY }
})

// The box itself has pointer-events: none so clicks pass through to elements below.
// Only the resize handles have pointer-events: all.
const boxStyle = computed(() => {
  if (!bounds.value) return {}
  return {
    position: 'absolute',
    left: bounds.value.x + 'px',
    top: bounds.value.y + 'px',
    width: bounds.value.w + 'px',
    height: bounds.value.h + 'px',
    pointerEvents: 'none',   // ← CRITICAL: let clicks pass through to elements
    zIndex: 99998,
  }
})

const HS = 9
const HALF = HS / 2
const handles = computed(() => {
  if (!bounds.value) return []
  const s = 1 / (props.zoom || 1)
  const size = HS * s
  const half = HALF * s
  return [
    { key: 'nw', style: { left: (-half)+'px', top: (-half)+'px', width: size+'px', height: size+'px', cursor: 'nwse-resize' } },
    { key: 'n',  style: { left: '50%', top: (-half)+'px', width: size+'px', height: size+'px', transform: 'translateX(-50%)', cursor: 'ns-resize' } },
    { key: 'ne', style: { right: (-half)+'px', top: (-half)+'px', width: size+'px', height: size+'px', cursor: 'nesw-resize' } },
    { key: 'e',  style: { right: (-half)+'px', top: '50%', width: size+'px', height: size+'px', transform: 'translateY(-50%)', cursor: 'ew-resize' } },
    { key: 'se', style: { right: (-half)+'px', bottom: (-half)+'px', width: size+'px', height: size+'px', cursor: 'nwse-resize' } },
    { key: 's',  style: { left: '50%', bottom: (-half)+'px', width: size+'px', height: size+'px', transform: 'translateX(-50%)', cursor: 'ns-resize' } },
    { key: 'sw', style: { left: (-half)+'px', bottom: (-half)+'px', width: size+'px', height: size+'px', cursor: 'nesw-resize' } },
    { key: 'w',  style: { left: (-half)+'px', top: '50%', width: size+'px', height: size+'px', transform: 'translateY(-50%)', cursor: 'ew-resize' } },
  ]
})

let resizeKey = null
let startBounds = null
let startMouse = { x: 0, y: 0 }
let startElementStates = []

function onHandleMousedown(e, key) {
  resizeKey = key
  startMouse = { x: e.clientX, y: e.clientY }
  startBounds = { ...bounds.value }
  // snapshot each selected element's initial rect
  startElementStates = props.selectedIds.map(id => {
    const el = props.elements.find(el => el.id === id)
    return el ? { id, x: el.x, y: el.y, width: el.width, height: el.height } : null
  }).filter(Boolean)
  showDim.value = true
  window.addEventListener('mousemove', onResizeMove)
  window.addEventListener('mouseup', onResizeUp)
}

function onResizeMove(e) {
  if (!resizeKey || !startBounds) return
  const z = props.zoom || 1
  const dx = (e.clientX - startMouse.x) / z
  const dy = (e.clientY - startMouse.y) / z
  let { x, y, w, h } = startBounds

  if (resizeKey.includes('e')) w = Math.max(10, startBounds.w + dx)
  if (resizeKey.includes('s')) h = Math.max(10, startBounds.h + dy)
  if (resizeKey.includes('w')) { x = startBounds.x + dx; w = Math.max(10, startBounds.w - dx) }
  if (resizeKey.includes('n')) { y = startBounds.y + dy; h = Math.max(10, startBounds.h - dy) }

  const scaleX = startBounds.w > 0 ? w / startBounds.w : 1
  const scaleY = startBounds.h > 0 ? h / startBounds.h : 1

  startElementStates.forEach(({ id, x: ex, y: ey, width: ew, height: eh }) => {
    emit('resize', {
      id,
      x: x + (ex - startBounds.x) * scaleX,
      y: y + (ey - startBounds.y) * scaleY,
      w: Math.max(10, ew * scaleX),
      h: Math.max(10, eh * scaleY),
    })
  })
}

function onResizeUp() {
  if (resizeKey) saveHistory()
  resizeKey = null
  showDim.value = false
  window.removeEventListener('mousemove', onResizeMove)
  window.removeEventListener('mouseup', onResizeUp)
}
</script>

<style scoped>
.selection-box {
  border: 1.5px solid #4F8EF7;
  box-sizing: border-box;
  pointer-events: none;  /* pass-through: clicks go to elements below */
}
.resize-handle {
  position: absolute;
  background: #fff;
  border: 1.5px solid #4F8EF7;
  border-radius: 2px;
  box-sizing: border-box;
  pointer-events: all;   /* handles DO capture events */
  z-index: 1;
  transition: background 0.1s, transform 0.1s;
}
.resize-handle:hover {
  background: #4F8EF7;
  transform: scale(1.2);
}
.dimension-tip {
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  background: #1a1a2e;
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
  font-family: 'Inter', monospace;
}
</style>
