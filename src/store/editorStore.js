import { reactive, computed } from 'vue'
import { v4 as uuidv4 } from 'uuid'

const createDefaultElement = (type, x, y) => {
  const base = {
    id: uuidv4(),
    type,
    x,
    y,
    width: 120,
    height: 40,
    rotation: 0,
    opacity: 100,
    zIndex: 0,
    name: type,
    visible: true,
    locked: false,
  }
  switch (type) {
    case 'rectangle':
      return { ...base, width: 160, height: 100, fill: '#4F8EF7', stroke: 'transparent', strokeWidth: 0, borderRadius: 4, name: 'Rectangle' }
    case 'circle':
      return { ...base, width: 100, height: 100, fill: '#F7874F', stroke: 'transparent', strokeWidth: 0, name: 'Circle' }
    case 'text':
      return { ...base, width: 200, height: 40, fill: 'transparent', stroke: 'transparent', strokeWidth: 0, text: '双击编辑文本', fontSize: 16, fontFamily: 'Inter, sans-serif', fontWeight: 'normal', fontStyle: 'normal', textDecoration: 'none', color: '#1a1a2e', textAlign: 'left', lineHeight: 1.5, name: 'Text' }
    case 'button':
      return { ...base, width: 140, height: 44, fill: '#4F8EF7', stroke: 'transparent', strokeWidth: 0, borderRadius: 8, text: '按钮', fontSize: 14, fontFamily: 'Inter, sans-serif', fontWeight: '600', color: '#ffffff', textAlign: 'center', name: 'Button' }
    case 'input':
      return { ...base, width: 220, height: 44, fill: '#ffffff', stroke: '#d1d5db', strokeWidth: 1.5, borderRadius: 8, placeholder: '请输入内容...', fontSize: 14, fontFamily: 'Inter, sans-serif', color: '#6b7280', name: 'Input' }
    case 'image':
      return { ...base, width: 200, height: 150, fill: '#f3f4f6', stroke: '#e5e7eb', strokeWidth: 1, src: '', borderRadius: 4, name: 'Image' }
    case 'card':
      return { ...base, width: 240, height: 160, fill: '#ffffff', stroke: '#e5e7eb', strokeWidth: 1, borderRadius: 12, shadow: true, name: 'Card' }
    case 'navbar':
      return { ...base, width: 375, height: 56, fill: '#ffffff', stroke: '#e5e7eb', strokeWidth: 1, borderRadius: 0, text: 'Navigation Bar', fontSize: 16, fontWeight: '600', color: '#1a1a2e', name: 'Navbar' }
    case 'icon':
      return { ...base, width: 40, height: 40, fill: '#4F8EF7', stroke: 'transparent', strokeWidth: 0, iconType: 'star', name: 'Icon' }
    case 'divider':
      return { ...base, width: 200, height: 2, fill: '#e5e7eb', stroke: 'transparent', strokeWidth: 0, borderRadius: 0, name: 'Divider' }
    case 'triangle':
      return { ...base, width: 100, height: 100, fill: '#10b981', stroke: 'transparent', strokeWidth: 0, name: 'Triangle' }
    default:
      return base
  }
}

const createDefaultPage = (name = '页面 1') => ({
  id: uuidv4(),
  name,
  elements: [],
  background: '#f8f9fa',
  width: 1440,
  height: 900,
})

export const store = reactive({
  pages: [createDefaultPage()],
  currentPageId: null,
  selectedIds: [],
  clipboard: null,
  history: [],
  historyIndex: -1,
  zoom: 1,
  panX: 0,
  panY: 0,
  tool: 'select',
  showGrid: true,
  snapToGrid: true,
  gridSize: 8,
  showRuler: true,
  shareLinks: {},
  activeShareId: null,
  isDragging: false,
  isResizing: false,
  editingTextId: null,
})

store.currentPageId = store.pages[0].id

export const currentPage = computed(() => store.pages.find(p => p.id === store.currentPageId) || store.pages[0])
export const selectedElements = computed(() => currentPage.value?.elements.filter(e => store.selectedIds.includes(e.id)) || [])
export const sortedElements = computed(() => {
  if (!currentPage.value) return []
  return [...currentPage.value.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
})

export function addElement(type, x = 100, y = 100) {
  const el = createDefaultElement(type, x, y)
  el.zIndex = currentPage.value.elements.length
  currentPage.value.elements.push(el)
  store.selectedIds = [el.id]
  saveHistory()
  return el
}

export function removeSelected() {
  if (!store.selectedIds.length) return
  currentPage.value.elements = currentPage.value.elements.filter(e => !store.selectedIds.includes(e.id))
  store.selectedIds = []
  saveHistory()
}

export function updateElement(id, props) {
  const el = currentPage.value?.elements.find(e => e.id === id)
  if (el) Object.assign(el, props)
}

export function selectElement(id, multi = false) {
  if (!id) { store.selectedIds = []; return }
  if (multi) {
    if (store.selectedIds.includes(id)) {
      store.selectedIds = store.selectedIds.filter(i => i !== id)
    } else {
      store.selectedIds = [...store.selectedIds, id]
    }
  } else {
    store.selectedIds = [id]
  }
}

export function duplicateSelected() {
  if (!store.selectedIds.length) return
  const newIds = []
  store.selectedIds.forEach(id => {
    const el = currentPage.value.elements.find(e => e.id === id)
    if (el) {
      const copy = { ...JSON.parse(JSON.stringify(el)), id: uuidv4(), x: el.x + 20, y: el.y + 20, zIndex: currentPage.value.elements.length, name: el.name + ' copy' }
      currentPage.value.elements.push(copy)
      newIds.push(copy.id)
    }
  })
  store.selectedIds = newIds
  saveHistory()
}

export function bringForward(id) {
  const el = currentPage.value.elements.find(e => e.id === id)
  if (el) { el.zIndex = (el.zIndex || 0) + 1 }
}

export function sendBackward(id) {
  const el = currentPage.value.elements.find(e => e.id === id)
  if (el) { el.zIndex = Math.max(0, (el.zIndex || 0) - 1) }
}

export function bringToFront(id) {
  const el = currentPage.value.elements.find(e => e.id === id)
  if (el) {
    const maxZ = Math.max(...currentPage.value.elements.map(e => e.zIndex || 0))
    el.zIndex = maxZ + 1
  }
}

export function sendToBack(id) {
  const el = currentPage.value.elements.find(e => e.id === id)
  if (el) { el.zIndex = 0 }
}

export function addPage() {
  const page = createDefaultPage(`页面 ${store.pages.length + 1}`)
  store.pages.push(page)
  store.currentPageId = page.id
  store.selectedIds = []
}

export function removePage(id) {
  if (store.pages.length <= 1) return
  const idx = store.pages.findIndex(p => p.id === id)
  store.pages = store.pages.filter(p => p.id !== id)
  if (store.currentPageId === id) {
    store.currentPageId = store.pages[Math.max(0, idx - 1)].id
  }
}

export function renamePage(id, name) {
  const page = store.pages.find(p => p.id === id)
  if (page) page.name = name
}

export function switchPage(id) {
  store.currentPageId = id
  store.selectedIds = []
}

export function saveHistory() {
  const snapshot = JSON.stringify({ pages: store.pages, currentPageId: store.currentPageId })
  if (store.historyIndex < store.history.length - 1) {
    store.history = store.history.slice(0, store.historyIndex + 1)
  }
  store.history.push(snapshot)
  if (store.history.length > 50) store.history.shift()
  store.historyIndex = store.history.length - 1
}

export function undo() {
  if (store.historyIndex <= 0) return
  store.historyIndex--
  const snapshot = JSON.parse(store.history[store.historyIndex])
  store.pages = snapshot.pages
  store.currentPageId = snapshot.currentPageId
  store.selectedIds = []
}

export function redo() {
  if (store.historyIndex >= store.history.length - 1) return
  store.historyIndex++
  const snapshot = JSON.parse(store.history[store.historyIndex])
  store.pages = snapshot.pages
  store.currentPageId = snapshot.currentPageId
  store.selectedIds = []
}

// Cloudflare Worker API 地址
const API_BASE = 'https://protoflow-api.protoflow-api.workers.dev'

/**
 * 生成分享链接（异步，数据存到 Cloudflare KV）
 * 返回 { url, shareId } 或抛出错误
 */
export async function generateShareLink() {
  const payload = {
    shareId: store.activeShareId || undefined,  // 已有 shareId 则更新同一条记录
    title: '高保真原型',
    pages: JSON.parse(JSON.stringify(store.pages)),
    createdAt: new Date().toISOString(),
  }

  const res = await fetch(`${API_BASE}/api/share`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error || `服务器错误 ${res.status}`)
  }

  const { shareId } = await res.json()
  store.activeShareId = shareId

  // 同时存本地做离线备份（可选）
  try {
    localStorage.setItem(`proto_share_${shareId}`, JSON.stringify(payload))
  } catch (_) {}

  const baseUrl = 'https://protoflow-editor.pages.dev'
  return { url: `${baseUrl}/#/preview/${shareId}`, shareId }
}

/**
 * 加载分享的原型数据（先查远端，降级查 localStorage）
 */
export async function loadSharedProject(shareId) {
  // 1. 优先从远端 KV 读取
  try {
    const res = await fetch(`${API_BASE}/api/share/${shareId}`)
    if (res.ok) {
      const { data } = await res.json()
      return data
    }
  } catch (_) {}

  // 2. 降级：从 localStorage 读取（兼容旧的本地分享）
  try {
    const raw = localStorage.getItem(`proto_share_${shareId}`)
    if (raw) return JSON.parse(raw)
  } catch (_) {}

  return null
}


export function copySelected() {
  store.clipboard = JSON.parse(JSON.stringify(store.selectedIds.map(id => currentPage.value.elements.find(e => e.id === id)).filter(Boolean)))
}

export function paste() {
  if (!store.clipboard?.length) return
  const newIds = []
  store.clipboard.forEach(el => {
    const copy = { ...JSON.parse(JSON.stringify(el)), id: uuidv4(), x: el.x + 20, y: el.y + 20, zIndex: currentPage.value.elements.length }
    currentPage.value.elements.push(copy)
    newIds.push(copy.id)
  })
  store.selectedIds = newIds
  saveHistory()
}

export function setZoom(z) {
  store.zoom = Math.min(Math.max(z, 0.1), 5)
}

export function resetView() {
  store.zoom = 1
  store.panX = 0
  store.panY = 0
}

export function groupSelected() {}
export function ungroupSelected() {}

saveHistory()
