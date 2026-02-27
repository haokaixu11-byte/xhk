<template>
  <div v-if="bounds" class="selection-box" :style="boxStyle" @mousedown.stop="onBoxMousedown">
    <!-- Resize handles -->
    <div v-for="h in handles" :key="h.key" class="resize-handle" :class="`handle-${h.key}`" :style="h.style" @mousedown.stop="onHandleMousedown($event, h.key)"></div>
    <!-- Dimension tooltip -->
    <div class="dimension-tip" v-if="showDim">{{ Math.round(bounds.w) }} × {{ Math.round(bounds.h) }}</div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
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

const boxStyle = computed(() => {
  if (!bounds.value) return {}
  return {
    position: 'absolute',
    left: bounds.value.x + 'px',
    top: bounds.value.y + 'px',
    width: bounds.value.w + 'px',
    height: bounds.value.h + 'px',
    pointerEvents: 'all',
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
    { key: 'n',  style: { left: '50%',         top: (-half)+'px', width: size+'px', height: size+'px', transform: 'translateX(-50%)', cursor: 'ns-resize' } },
    { key: 'ne', style: { right: (-half)+'px', top: (-half)+'px', width: size+'px', height: size+'px', cursor: 'nesw-resize' } },
    { key: 'e',  style: { right: (-half)+'px', top: '50%',        width: size+'px', height: size+'px', transform: 'translateY(-50%)', cursor: 'ew-resize' } },
    { key: 'se', style: { right: (-half)+'px', bottom: (-half)+'px', width: size+'px', height: size+'px', cursor: 'nwse-resize' } },
    { key: 's',  style: { left: '50%',         bottom: (-half)+'px', width: size+'px', height: size+'px', transform: 'translateX(-50%)', cursor: 'ns-resize' } },
    { key: 'sw', style: { left: (-half)+'px',  bottom: (-half)+'px', width: size+'px', height: size+'px', cursor: 'nesw-resize' } },
    { key: 'w',  style: { left: (-half)+'px',  top: '50%',        width: size+'px', height: size+'px', transform: 'translateY(-50%)', cursor: 'ew-resize' } },
  ]
})

let resizeKey = null
let startBounds = null
let startMouse = { x: 0, y: 0 }

function onHandleMousedown(e, key) {
  e.stopPropagation()
  resizeKey = key
  startMouse = { x: e.clientX, y: e.clientY }
  startBounds = { ...bounds.value }
  showDim.value = true
  window.addEventListener('mousemove', onResizeMove)
  window.addEventListener('mouseup', onResizeUp)
}

function onBoxMousedown(e) {}

function onResizeMove(e) {
  if (!resizeKey || !startBounds) return
  const z = props.zoom || 1
  const dx = (e.clientX - startMouse.x) / z
  const dy = (e.clientY - startMouse.y) / z
  let { x, y, w, h } = startBounds
  if (resizeKey.includes('e')) w = Math.max(10, w + dx)
  if (resizeKey.includes('s')) h = Math.max(10, h + dy)
  if (resizeKey.includes('w')) { x = x + dx; w = Math.max(10, w - dx) }
  if (resizeKey.includes('n')) { y = y + dy; h = Math.max(10, h - dy) }
  props.selectedIds.forEach(id => {
    const el = props.elements.find(el => el.id === id)
    if (!el) return
    const scaleX = startBounds.w > 0 ? w / startBounds.w : 1
    const scaleY = startBounds.h > 0 ? h / startBounds.h : 1
    emit('resize', {
      id,
      x: x + (el.x - startBounds.x) * scaleX,
      y: y + (el.y - startBounds.y) * scaleY,
      w: Math.max(10, el.width * scaleX),
      h: Math.max(10, el.height * scaleY),
    })
  })
}

function onResizeUp() {
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
  pointer-events: none;
}
.resize-handle {
  position: absolute;
  background: #fff;
  border: 1.5px solid #4F8EF7;
  border-radius: 2px;
  box-sizing: border-box;
  pointer-events: all;
  z-index: 1;
  transition: background 0.1s;
}
.resize-handle:hover { background: #4F8EF7; }
.dimension-tip {
  position: absolute;
  bottom: -22px;
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
