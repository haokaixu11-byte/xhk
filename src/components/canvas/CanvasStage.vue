<template>
  <div class="canvas-stage" ref="stageRef" @mousedown="onStageMousedown" @mousemove="onMouseMove" @mouseup="onMouseUp" @wheel="onWheel" @contextmenu.prevent="onContextMenu" @dblclick="onDblClick">
    <!-- Grid -->
    <svg v-if="store.showGrid" class="canvas-grid" :width="stageW" :height="stageH">
      <defs>
        <pattern :id="`grid-small-${instanceId}`" :width="gridSmall" :height="gridSmall" patternUnits="userSpaceOnUse">
          <path :d="`M ${gridSmall} 0 L 0 0 0 ${gridSmall}`" fill="none" stroke="#e8e8f0" stroke-width="0.5"/>
        </pattern>
        <pattern :id="`grid-large-${instanceId}`" :width="gridLarge" :height="gridLarge" patternUnits="userSpaceOnUse">
          <rect :width="gridLarge" :height="gridLarge" :fill="`url(#grid-small-${instanceId})`"/>
          <path :d="`M ${gridLarge} 0 L 0 0 0 ${gridLarge}`" fill="none" stroke="#d0d0e0" stroke-width="1"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" :fill="`url(#grid-large-${instanceId})`"/>
    </svg>

    <!-- Canvas transform wrapper -->
    <div class="canvas-transform" :style="transformStyle">
      <!-- Page background -->
      <div class="page-canvas" :style="pageStyle" @mousedown="onPageBgMousedown">
        <!-- Elements -->
        <template v-for="el in sortedElements" :key="el.id">
          <ElementRenderer
            :element="el"
            :selected="store.selectedIds.includes(el.id)"
            :editing="store.editingTextId === el.id"
            :zoom="store.zoom"
            @mousedown.stop="onElementMousedown($event, el)"
            @dblclick.stop="onElementDblClick(el)"
            @update="onElementUpdate(el.id, $event)"
            @commit="onElementCommit(el.id, $event)"
            @endEdit="store.editingTextId = null"
          />
        </template>

        <!-- Selection Box -->
        <SelectionBox v-if="store.selectedIds.length > 0 && !store.editingTextId" :selectedIds="store.selectedIds" :elements="currentPage.elements" :zoom="store.zoom" @resize="onSelectionResize" @move="onSelectionMove" />

        <!-- Rubber band selection -->
        <div v-if="rubberBand.active" class="rubber-band" :style="rubberBandStyle"></div>
      </div>
    </div>

    <!-- Context Menu -->
    <ContextMenu v-if="contextMenu.show" :x="contextMenu.x" :y="contextMenu.y" :hasSelection="store.selectedIds.length > 0" @close="contextMenu.show = false" @action="handleContextAction" />

    <!-- Zoom indicator -->
    <div class="zoom-indicator">{{ Math.round(store.zoom * 100) }}%</div>

    <!-- Quick zoom controls -->
    <div class="zoom-controls">
      <button @click="zoomIn" title="放大">+</button>
      <button @click="resetZoom" title="重置">⊙</button>
      <button @click="zoomOut" title="缩小">−</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onUnmounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { store, currentPage, sortedElements, selectElement, updateElement, removeSelected, duplicateSelected, copySelected, paste, setZoom, undo, redo, saveHistory, bringToFront, sendToBack, bringForward, sendBackward, addElement } from '../../store/editorStore.js'
import ElementRenderer from './ElementRenderer.vue'
import SelectionBox from './SelectionBox.vue'
import ContextMenu from './ContextMenu.vue'

const instanceId = uuidv4().slice(0,8)
const stageRef = ref(null)
const stageW = ref(window.innerWidth)
const stageH = ref(window.innerHeight)

const gridSmall = computed(() => store.gridSize * store.zoom)
const gridLarge = computed(() => store.gridSize * 8 * store.zoom)

const transformStyle = computed(() => ({
  transform: `translate(${store.panX}px, ${store.panY}px) scale(${store.zoom})`,
  transformOrigin: '0 0',
}))

const pageStyle = computed(() => ({
  width: (currentPage.value?.width || 1440) + 'px',
  height: (currentPage.value?.height || 900) + 'px',
  background: currentPage.value?.background || '#ffffff',
  position: 'relative',
  overflow: 'hidden',
}))

const contextMenu = reactive({ show: false, x: 0, y: 0 })
const rubberBand = reactive({ active: false, startX: 0, startY: 0, x: 0, y: 0, w: 0, h: 0 })
const rubberBandStyle = computed(() => ({
  position: 'absolute',
  left: rubberBand.x + 'px',
  top: rubberBand.y + 'px',
  width: rubberBand.w + 'px',
  height: rubberBand.h + 'px',
  border: '1.5px dashed #4F8EF7',
  background: 'rgba(79,142,247,0.08)',
  pointerEvents: 'none',
  zIndex: 99999,
}))

let isPanning = false
let panStart = { x: 0, y: 0 }
let isDraggingElement = false
let didDrag = false   // true if mouse actually moved while dragging element
let dragStart = { x: 0, y: 0 }
let elementsStartPos = []
let spaceDown = false
let rubberBandStartedOnElement = false

function screenToCanvas(sx, sy) {
  const rect = stageRef.value?.getBoundingClientRect() || { left: 0, top: 0 }
  return {
    x: (sx - rect.left - store.panX) / store.zoom,
    y: (sy - rect.top - store.panY) / store.zoom,
  }
}

function onStageMousedown(e) {
  if (e.button === 1 || (e.button === 0 && spaceDown)) {
    isPanning = true
    panStart = { x: e.clientX - store.panX, y: e.clientY - store.panY }
    e.preventDefault()
    return
  }
  if (e.button === 0 && store.tool === 'select') {
    rubberBandStartedOnElement = false
    const cp = screenToCanvas(e.clientX, e.clientY)
    rubberBand.active = true
    rubberBand.startX = cp.x
    rubberBand.startY = cp.y
    rubberBand.x = cp.x
    rubberBand.y = cp.y
    rubberBand.w = 0
    rubberBand.h = 0
  }
}

function onPageBgMousedown(e) {
  // Clicking the page background (not an element) - deselect all & start rubber-band
  // Do NOT stopPropagation so onStageMousedown also fires for rubber-band
  if (!isDraggingElement && !spaceDown) {
    selectElement(null)
    store.editingTextId = null
  }
  didDrag = false
}

function onElementMousedown(e, el) {
  if (e.button !== 0) return
  if (el.locked) return
  if (store.editingTextId === el.id) return

  // Prevent rubber-band from starting when clicking an element
  rubberBandStartedOnElement = true
  rubberBand.active = false

  if (!store.selectedIds.includes(el.id)) {
    selectElement(el.id, e.shiftKey || e.metaKey || e.ctrlKey)
  } else if (e.shiftKey || e.metaKey || e.ctrlKey) {
    selectElement(el.id, true)
    return
  }

  isDraggingElement = true
  didDrag = false
  store.isDragging = true
  dragStart = { x: e.clientX, y: e.clientY }
  elementsStartPos = store.selectedIds.map(id => {
    const found = currentPage.value.elements.find(e2 => e2.id === id)
    return found ? { id, x: found.x, y: found.y } : null
  }).filter(Boolean)

  const onUp = () => {
    if (isDraggingElement && didDrag) saveHistory()
    isDraggingElement = false
    didDrag = false
    store.isDragging = false
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mouseup', onUp)
}

function onElementDblClick(el) {
  if (['text', 'button', 'navbar', 'input'].includes(el.type)) {
    store.editingTextId = el.id
  }
}

function onDblClick(e) {}

function onElementUpdate(id, props) {
  updateElement(id, props)
}
function onElementCommit(id, props) {
  updateElement(id, props)
  saveHistory()
}

function onMouseMove(e) {
  if (isPanning) {
    store.panX = e.clientX - panStart.x
    store.panY = e.clientY - panStart.y
    return
  }
  if (isDraggingElement) {
    const dx = (e.clientX - dragStart.x) / store.zoom
    const dy = (e.clientY - dragStart.y) / store.zoom
    // Only count as actual drag if moved more than 2px
    if (Math.abs(e.clientX - dragStart.x) > 2 || Math.abs(e.clientY - dragStart.y) > 2) {
      didDrag = true
    }
    elementsStartPos.forEach(({ id, x, y }) => {
      let nx = x + dx
      let ny = y + dy
      if (store.snapToGrid) {
        nx = Math.round(nx / store.gridSize) * store.gridSize
        ny = Math.round(ny / store.gridSize) * store.gridSize
      }
      updateElement(id, { x: nx, y: ny })
    })
    return
  }
  if (rubberBand.active && !rubberBandStartedOnElement) {
    const cp = screenToCanvas(e.clientX, e.clientY)
    const x = Math.min(cp.x, rubberBand.startX)
    const y = Math.min(cp.y, rubberBand.startY)
    const w = Math.abs(cp.x - rubberBand.startX)
    const h = Math.abs(cp.y - rubberBand.startY)
    rubberBand.x = x
    rubberBand.y = y
    rubberBand.w = w
    rubberBand.h = h
  }
}

function onMouseUp(e) {
  if (isPanning) { isPanning = false; return }
  if (rubberBand.active) {
    if (!rubberBandStartedOnElement && (rubberBand.w > 5 || rubberBand.h > 5)) {
      const ids = currentPage.value.elements.filter(el => {
        return el.x < rubberBand.x + rubberBand.w &&
          el.x + el.width > rubberBand.x &&
          el.y < rubberBand.y + rubberBand.h &&
          el.y + el.height > rubberBand.y
      }).map(el => el.id)
      store.selectedIds = ids
    }
    rubberBand.active = false
    rubberBand.w = 0
    rubberBand.h = 0
    rubberBandStartedOnElement = false
  }
}

function onWheel(e) {
  e.preventDefault()
  if (e.ctrlKey || e.metaKey) {
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    const rect = stageRef.value.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const newZoom = Math.min(Math.max(store.zoom * delta, 0.1), 5)
    store.panX = mx - (mx - store.panX) * (newZoom / store.zoom)
    store.panY = my - (my - store.panY) * (newZoom / store.zoom)
    store.zoom = newZoom
  } else {
    store.panX -= e.deltaX
    store.panY -= e.deltaY
  }
}

function onContextMenu(e) {
  contextMenu.show = true
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
}

function handleContextAction(action) {
  contextMenu.show = false
  switch (action) {
    case 'copy': copySelected(); break
    case 'paste': paste(); break
    case 'duplicate': duplicateSelected(); break
    case 'delete': removeSelected(); break
    case 'bringForward': store.selectedIds.forEach(id => bringForward(id)); break
    case 'sendBackward': store.selectedIds.forEach(id => sendBackward(id)); break
    case 'bringToFront': store.selectedIds.forEach(id => bringToFront(id)); break
    case 'sendToBack': store.selectedIds.forEach(id => sendToBack(id)); break
  }
}

function onSelectionResize({ id, x, y, w, h }) {
  updateElement(id, { x, y, width: w, height: h })
}

function onSelectionMove({ dx, dy }) {
  store.selectedIds.forEach(id => {
    const el = currentPage.value.elements.find(e => e.id === id)
    if (el) updateElement(id, { x: el.x + dx, y: el.y + dy })
  })
  saveHistory()
}

function zoomIn() { setZoom(store.zoom * 1.2) }
function zoomOut() { setZoom(store.zoom / 1.2) }
function resetZoom() { store.zoom = 1; store.panX = 40; store.panY = 40 }

// Check if the event target is a text input / textarea / contenteditable
// If so, skip canvas keyboard shortcuts so typing doesn't delete elements
function isInputFocused() {
  const el = document.activeElement
  if (!el) return false
  const tag = el.tagName.toLowerCase()
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return true
  if (el.isContentEditable) return true
  return false
}

function onKeydown(e) {
  // Space — only when not typing anywhere
  if (e.code === 'Space' && !isInputFocused()) { spaceDown = true; e.preventDefault() }
  
  // Undo/Redo — allow even in inputs (standard browser behavior via ctrl/meta)
  if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) { undo(); e.preventDefault() }
  if ((e.metaKey || e.ctrlKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) { redo(); e.preventDefault() }
  
  // Copy / Paste / Duplicate — skip if typing in an input
  if (!isInputFocused()) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'c') { copySelected(); e.preventDefault() }
    if ((e.metaKey || e.ctrlKey) && e.key === 'v') {
      // Try system clipboard first (images from outside); fall back to internal clipboard
      pasteFromSystemClipboard().then(handled => {
        if (!handled) paste()
      })
      e.preventDefault()
    }
    if ((e.metaKey || e.ctrlKey) && e.key === 'd') { duplicateSelected(); e.preventDefault() }
  }

  // Delete / Backspace — ONLY when not focused in any input AND not editing a canvas text element
  if ((e.key === 'Delete' || e.key === 'Backspace') && !store.editingTextId && !isInputFocused()) {
    removeSelected()
    e.preventDefault()
  }

  // Escape — always clears selection & text editing
  if (e.key === 'Escape') {
    store.selectedIds = []
    store.editingTextId = null
  }

  // Arrow keys — only when NOT focused in any input
  if (!isInputFocused() && !store.editingTextId) {
    const step = e.shiftKey ? 10 : 1
    if (e.key === 'ArrowLeft') {
      store.selectedIds.forEach(id => { const el = currentPage.value.elements.find(e2 => e2.id === id); if (el) updateElement(id, { x: el.x - step }) })
      e.preventDefault()
    }
    if (e.key === 'ArrowRight') {
      store.selectedIds.forEach(id => { const el = currentPage.value.elements.find(e2 => e2.id === id); if (el) updateElement(id, { x: el.x + step }) })
      e.preventDefault()
    }
    if (e.key === 'ArrowUp') {
      store.selectedIds.forEach(id => { const el = currentPage.value.elements.find(e2 => e2.id === id); if (el) updateElement(id, { y: el.y - step }) })
      e.preventDefault()
    }
    if (e.key === 'ArrowDown') {
      store.selectedIds.forEach(id => { const el = currentPage.value.elements.find(e2 => e2.id === id); if (el) updateElement(id, { y: el.y + step }) })
      e.preventDefault()
    }
  }
}

function onKeyup(e) {
  if (e.code === 'Space') spaceDown = false
}

function onResize() {
  stageW.value = window.innerWidth
  stageH.value = window.innerHeight
}

/**
 * Handle system paste event (fired by browser when Ctrl+V is pressed
 * while the document has focus). Intercepts image/file items from
 * the DataTransfer and places them on the canvas as image elements.
 * Also called from onKeydown as a fallback via navigator.clipboard.read().
 */
function onPaste(e) {
  // Skip if user is typing in a real input/textarea (not canvas editing)
  if (isInputFocused()) return
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      const file = item.getAsFile()
      if (!file) continue
      const reader = new FileReader()
      reader.onload = (ev) => {
        const dataUrl = ev.target.result
        placeImageOnCanvas(dataUrl, file.name || 'pasted-image')
      }
      reader.readAsDataURL(file)
      return  // only handle first image
    }
  }
}

/**
 * Async fallback: read system clipboard via Permissions API.
 * Returns true if an image was found and placed, false otherwise.
 */
async function pasteFromSystemClipboard() {
  try {
    if (!navigator.clipboard?.read) return false
    const clipItems = await navigator.clipboard.read()
    for (const clipItem of clipItems) {
      for (const type of clipItem.types) {
        if (type.startsWith('image/')) {
          const blob = await clipItem.getType(type)
          const reader = new FileReader()
          await new Promise((resolve) => {
            reader.onload = (ev) => {
              placeImageOnCanvas(ev.target.result, 'clipboard-image')
              resolve()
            }
            reader.readAsDataURL(blob)
          })
          return true
        }
      }
    }
  } catch (_) {
    // Permission denied or API not available — handled by caller falling back to paste()
  }
  return false
}

/**
 * Place a DataURL image onto the canvas, centered in the current viewport.
 * Auto-scales to fit within the page while keeping the natural aspect ratio.
 */
function placeImageOnCanvas(dataUrl, name) {
  const img = new Image()
  img.onload = () => {
    const page = currentPage.value
    const pageW = page?.width || 1440
    const pageH = page?.height || 900

    // Scale to at most half the page, preserving aspect ratio
    const maxW = Math.min(img.naturalWidth, pageW * 0.6)
    const maxH = Math.min(img.naturalHeight, pageH * 0.6)
    const scale = Math.min(maxW / img.naturalWidth, maxH / img.naturalHeight, 1)
    const w = Math.round(img.naturalWidth * scale)
    const h = Math.round(img.naturalHeight * scale)

    // Center in the visible viewport area
    const viewCenterX = (stageW.value / 2 - store.panX) / store.zoom
    const viewCenterY = (stageH.value / 2 - store.panY) / store.zoom
    const x = Math.round(Math.max(0, Math.min(viewCenterX - w / 2, pageW - w)))
    const y = Math.round(Math.max(0, Math.min(viewCenterY - h / 2, pageH - h)))

    const el = addElement('image', x, y)
    updateElement(el.id, {
      src: dataUrl,
      width: w,
      height: h,
      name: name.replace(/\.[^.]+$/, '') || '图片',
    })
  }
  img.src = dataUrl
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('keyup', onKeyup)
  window.addEventListener('resize', onResize)
  window.addEventListener('paste', onPaste)
  store.panX = 40
  store.panY = 40
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('keyup', onKeyup)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('paste', onPaste)
})
</script>

<style scoped>
.canvas-stage {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #f0f0f5;
  cursor: default;
  user-select: none;
}
.canvas-grid {
  position: absolute;
  top: 0; left: 0;
  pointer-events: none;
  z-index: 0;
}
.canvas-transform {
  position: absolute;
  top: 0; left: 0;
  z-index: 1;
}
.page-canvas {
  box-shadow: 0 4px 40px rgba(0,0,0,0.18), 0 1px 4px rgba(0,0,0,0.08);
  border-radius: 2px;
}
.rubber-band {
  border-radius: 2px;
}
.zoom-indicator {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(30,30,50,0.75);
  color: #fff;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  pointer-events: none;
  z-index: 1000;
  font-family: 'Inter', monospace;
  backdrop-filter: blur(4px);
}
.zoom-controls {
  position: absolute;
  bottom: 16px;
  right: 24px;
  display: flex;
  gap: 4px;
  z-index: 1000;
}
.zoom-controls button {
  width: 32px;
  height: 32px;
  border: 1px solid #e0e0e8;
  background: rgba(255,255,255,0.92);
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: #444;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
  backdrop-filter: blur(8px);
}
.zoom-controls button:hover {
  background: #fff;
  border-color: #4F8EF7;
  color: #4F8EF7;
}
</style>
