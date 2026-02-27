<template>
  <aside class="left-panel">
    <!-- Tabs -->
    <div class="panel-tabs">
      <button :class="{ active: tab === 'components' }" @click="tab = 'components'">组件</button>
      <button :class="{ active: tab === 'layers' }" @click="tab = 'layers'">图层</button>
      <button :class="{ active: tab === 'pages' }" @click="tab = 'pages'">页面</button>
    </div>

    <!-- Components Tab -->
    <div v-if="tab === 'components'" class="tab-content">
      <div class="section-title">基础图形</div>
      <div class="component-grid">
        <div v-for="c in basicComponents" :key="c.type" class="comp-item" draggable="true" @dragstart="onDragStart($event, c.type)" @click="addComp(c.type)" :title="c.label">
          <div class="comp-icon">
            <component :is="c.icon" />
          </div>
          <span>{{ c.label }}</span>
        </div>
      </div>
      <div class="section-title">UI 组件</div>
      <div class="component-grid">
        <div v-for="c in uiComponents" :key="c.type" class="comp-item" draggable="true" @dragstart="onDragStart($event, c.type)" @click="addComp(c.type)" :title="c.label">
          <div class="comp-icon">
            <component :is="c.icon" />
          </div>
          <span>{{ c.label }}</span>
        </div>
      </div>
    </div>

    <!-- Layers Tab -->
    <div v-else-if="tab === 'layers'" class="tab-content layers-tab">
      <div class="layers-search">
        <input v-model="layerSearch" placeholder="搜索图层..." />
      </div>
      <div class="layers-list">
        <div v-if="!filteredLayers.length" class="empty-hint">暂无图层</div>
        <div v-for="el in filteredLayers" :key="el.id" class="layer-item" :class="{ selected: store.selectedIds.includes(el.id), hidden: !el.visible, locked: el.locked }" @click="onLayerClick($event, el)" @dblclick="startRenameLayer(el)">
          <div class="layer-icon">{{ getLayerIcon(el.type) }}</div>
          <div class="layer-name" v-if="renamingId !== el.id">{{ el.name }}</div>
          <input v-else class="layer-name-input" v-model="renameValue" @blur="commitRename(el)" @keydown.enter="commitRename(el)" @keydown.escape="renamingId = null" @click.stop @mousedown.stop ref="renameInput" />
          <div class="layer-actions">
            <span class="layer-action" @click.stop="toggleVisible(el)" :title="el.visible ? '隐藏' : '显示'">{{ el.visible !== false ? '👁' : '🙈' }}</span>
            <span class="layer-action" @click.stop="toggleLock(el)" :title="el.locked ? '解锁' : '锁定'">{{ el.locked ? '🔒' : '🔓' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pages Tab -->
    <div v-else-if="tab === 'pages'" class="tab-content pages-tab">
      <div class="pages-list">
        <div v-for="page in store.pages" :key="page.id" class="page-item" :class="{ active: store.currentPageId === page.id }" @click="switchPage(page.id)" @dblclick="startRenamePage(page)">
          <div class="page-thumb">
            <svg viewBox="0 0 40 28" width="40" height="28">
              <rect width="40" height="28" rx="2" :fill="page.background || '#f8f9fa'"/>
              <rect x="4" y="4" width="32" height="2" rx="1" fill="#d1d5db"/>
              <rect x="4" y="10" width="24" height="2" rx="1" fill="#e5e7eb"/>
              <rect x="4" y="16" width="28" height="2" rx="1" fill="#e5e7eb"/>
              <rect x="4" y="22" width="16" height="2" rx="1" fill="#e5e7eb"/>
            </svg>
          </div>
          <div class="page-info">
            <div class="page-name" v-if="renamingPageId !== page.id">{{ page.name }}</div>
            <input v-else class="page-name-input" v-model="renamePageValue" @blur="commitRenamePage(page)" @keydown.enter="commitRenamePage(page)" @keydown.escape="renamingPageId = null" @click.stop @mousedown.stop />
            <div class="page-meta">{{ page.elements?.length || 0 }} 个元素</div>
          </div>
          <button class="page-delete-btn" v-if="store.pages.length > 1" @click.stop="removePage(page.id)" title="删除页面">×</button>
        </div>
      </div>
      <button class="add-page-btn" @click="addPage">+ 新建页面</button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, nextTick, h } from 'vue'
import { store, currentPage, addElement, selectElement, updateElement, addPage, removePage, switchPage, renamePage } from '../../store/editorStore.js'

const tab = ref('components')
const layerSearch = ref('')
const renamingId = ref(null)
const renameValue = ref('')
const renameInput = ref(null)
const renamingPageId = ref(null)
const renamePageValue = ref('')

const RectIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('rect', { x: 2, y: 4, width: 16, height: 12, rx: 2, fill: '#4F8EF7' })])
const CircleIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('circle', { cx: 10, cy: 10, r: 8, fill: '#F7874F' })])
const TriangleIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('polygon', { points: '10,2 18,18 2,18', fill: '#10b981' })])
const TextIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('text', { x: 3, y: 15, fontSize: 14, fontWeight: 700, fill: '#1a1a2e', fontFamily: 'serif' }, 'T')])
const DividerIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('line', { x1: 1, y1: 10, x2: 19, y2: 10, stroke: '#9ca3af', strokeWidth: 2 })])
const ButtonIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('rect', { x: 1, y: 5, width: 18, height: 10, rx: 4, fill: '#4F8EF7' }), h('text', { x: 5.5, y: 13, fontSize: 7, fill: '#fff', fontFamily: 'sans-serif', fontWeight: 700 }, 'BTN')])
const InputIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('rect', { x: 1, y: 5, width: 18, height: 10, rx: 3, fill: '#fff', stroke: '#9ca3af', strokeWidth: 1.5 }), h('line', { x1: 4, y1: 10, x2: 9, y2: 10, stroke: '#d1d5db', strokeWidth: 1 })])
const CardIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('rect', { x: 1, y: 2, width: 18, height: 16, rx: 3, fill: '#fff', stroke: '#e5e7eb', strokeWidth: 1.5 }), h('rect', { x: 1, y: 2, width: 18, height: 7, rx: 3, fill: '#4F8EF7' })])
const NavbarIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('rect', { x: 0, y: 3, width: 20, height: 14, fill: '#fff', stroke: '#e5e7eb', strokeWidth: 1 }), h('line', { x1: 3, y1: 10, x2: 8, y2: 10, stroke: '#4F8EF7', strokeWidth: 2 }), h('line', { x1: 12, y1: 10, x2: 17, y2: 10, stroke: '#9ca3af', strokeWidth: 1.5 })])
const ImageIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('rect', { x: 1, y: 3, width: 18, height: 14, rx: 2, fill: '#f3f4f6', stroke: '#e5e7eb', strokeWidth: 1 }), h('circle', { cx: 7, cy: 8, r: 2, fill: '#fbbf24' }), h('polygon', { points: '2,17 8,10 13,14 16,11 19,17', fill: '#a3e635' })])
const IconIcon = () => h('svg', { viewBox: '0 0 20 20', width: 20, height: 20 }, [h('polygon', { points: '10,2 12.5,7.5 18,8.5 14,12.5 15,18 10,15 5,18 6,12.5 2,8.5 7.5,7.5', fill: '#4F8EF7' })])

const basicComponents = [
  { type: 'rectangle', label: '矩形', icon: RectIcon },
  { type: 'circle', label: '圆形', icon: CircleIcon },
  { type: 'triangle', label: '三角', icon: TriangleIcon },
  { type: 'text', label: '文本', icon: TextIcon },
  { type: 'divider', label: '分割线', icon: DividerIcon },
  { type: 'image', label: '图片', icon: ImageIcon },
]
const uiComponents = [
  { type: 'button', label: '按钮', icon: ButtonIcon },
  { type: 'input', label: '输入框', icon: InputIcon },
  { type: 'card', label: '卡片', icon: CardIcon },
  { type: 'navbar', label: '导航栏', icon: NavbarIcon },
  { type: 'icon', label: '图标', icon: IconIcon },
]

const filteredLayers = computed(() => {
  const els = [...(currentPage.value?.elements || [])].reverse()
  if (!layerSearch.value) return els
  return els.filter(e => e.name?.toLowerCase().includes(layerSearch.value.toLowerCase()))
})

function getLayerIcon(type) {
  const icons = { rectangle: '▭', circle: '○', triangle: '△', text: 'T', button: '⊡', input: '⌨', card: '▤', navbar: '☰', image: '🖼', icon: '★', divider: '─' }
  return icons[type] || '▭'
}

function onLayerClick(e, el) {
  selectElement(el.id, e.shiftKey || e.metaKey)
}

function startRenameLayer(el) {
  renamingId.value = el.id
  renameValue.value = el.name
  nextTick(() => renameInput.value?.[0]?.focus())
}

function commitRename(el) {
  if (renameValue.value.trim()) updateElement(el.id, { name: renameValue.value.trim() })
  renamingId.value = null
}

function toggleVisible(el) {
  updateElement(el.id, { visible: el.visible === false ? true : false })
}

function toggleLock(el) {
  updateElement(el.id, { locked: !el.locked })
}

function startRenamePage(page) {
  renamingPageId.value = page.id
  renamePageValue.value = page.name
}

function commitRenamePage(page) {
  if (renamePageValue.value.trim()) renamePage(page.id, renamePageValue.value.trim())
  renamingPageId.value = null
}

function addComp(type) {
  addElement(type, 100 + Math.random() * 60, 100 + Math.random() * 60)
}

function onDragStart(e, type) {
  e.dataTransfer.setData('comp_type', type)
}
</script>

<style scoped>
.left-panel {
  width: 220px;
  min-width: 220px;
  height: 100%;
  background: #18182a;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #2a2a3e;
  overflow: hidden;
}
.panel-tabs {
  display: flex;
  border-bottom: 1px solid #2a2a3e;
  flex-shrink: 0;
}
.panel-tabs button {
  flex: 1;
  padding: 10px 4px;
  background: none;
  border: none;
  color: #8888aa;
  font-size: 12px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s;
  font-family: 'Inter', sans-serif;
}
.panel-tabs button.active {
  color: #4F8EF7;
  border-bottom-color: #4F8EF7;
}
.tab-content { flex: 1; overflow-y: auto; padding: 12px 10px; }
.section-title { font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.06em; margin: 10px 0 8px; padding: 0 2px; font-weight: 600; }
.component-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 10px; }
.comp-item { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 8px 4px; background: #1e1e30; border: 1px solid #2a2a3e; border-radius: 8px; cursor: pointer; transition: all 0.15s; user-select: none; }
.comp-item:hover { background: #252540; border-color: #4F8EF7; transform: translateY(-1px); }
.comp-item span { font-size: 10px; color: #9ca3af; text-align: center; }
.comp-icon { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; }
/* Layers */
.layers-tab { padding: 8px; }
.layers-search input { width: 100%; padding: 7px 10px; background: #1e1e30; border: 1px solid #2a2a3e; border-radius: 6px; color: #e0e0f0; font-size: 12px; outline: none; box-sizing: border-box; }
.layers-list { margin-top: 8px; display: flex; flex-direction: column; gap: 2px; }
.empty-hint { text-align: center; color: #555; font-size: 12px; padding: 20px 0; }
.layer-item { display: flex; align-items: center; gap: 6px; padding: 6px 8px; border-radius: 6px; cursor: pointer; transition: background 0.1s; color: #c0c0d8; font-size: 12px; }
.layer-item:hover { background: #1e1e30; }
.layer-item.selected { background: #1e2a4a; color: #4F8EF7; }
.layer-item.hidden { opacity: 0.5; }
.layer-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.layer-name-input { flex: 1; background: #252540; border: 1px solid #4F8EF7; color: #e0e0f0; border-radius: 4px; padding: 2px 6px; font-size: 12px; outline: none; min-width: 0; }
.layer-icon { font-size: 14px; width: 20px; flex-shrink: 0; text-align: center; }
.layer-actions { display: flex; gap: 4px; flex-shrink: 0; }
.layer-action { cursor: pointer; font-size: 12px; opacity: 0.6; transition: opacity 0.1s; }
.layer-action:hover { opacity: 1; }
/* Pages */
.pages-tab { padding: 8px; }
.pages-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px; }
.page-item { display: flex; align-items: center; gap: 8px; padding: 8px; border-radius: 8px; cursor: pointer; border: 1.5px solid transparent; transition: all 0.15s; background: #1e1e30; }
.page-item:hover { background: #252540; }
.page-item.active { border-color: #4F8EF7; background: #1e2a4a; }
.page-thumb { flex-shrink: 0; border-radius: 3px; overflow: hidden; }
.page-info { flex: 1; min-width: 0; }
.page-name { font-size: 12px; color: #e0e0f0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.page-name-input { width: 100%; background: #252540; border: 1px solid #4F8EF7; color: #e0e0f0; border-radius: 4px; padding: 2px 4px; font-size: 12px; outline: none; }
.page-meta { font-size: 10px; color: #6b7280; margin-top: 2px; }
.page-delete-btn { width: 20px; height: 20px; border: none; background: none; color: #6b7280; cursor: pointer; font-size: 16px; border-radius: 4px; padding: 0; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-delete-btn:hover { color: #ef4444; background: #2a1515; }
.add-page-btn { width: 100%; padding: 9px; background: #1e1e30; border: 1.5px dashed #2a2a3e; border-radius: 8px; color: #6b7280; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.add-page-btn:hover { border-color: #4F8EF7; color: #4F8EF7; background: #1e2a4a; }
</style>
