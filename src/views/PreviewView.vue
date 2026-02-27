<template>
  <div class="preview-app" :class="{ 'show-annotations': showAnnotations }">
    <!-- Loading State -->
    <div v-if="loading" class="preview-loading">
      <div class="loading-spinner"></div>
      <p>加载原型中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="preview-error">
      <div class="error-icon">⚠️</div>
      <h2>原型不存在</h2>
      <p>链接可能已过期或无效，请联系原型创建者重新生成链接。</p>
      <button @click="goBack">返回编辑器</button>
    </div>

    <!-- Preview Content -->
    <template v-else-if="project">
      <!-- Preview Toolbar -->
      <div class="preview-toolbar">
        <div class="preview-logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <rect width="24" height="24" rx="6" fill="#4F8EF7"/>
            <rect x="4" y="4" width="7" height="7" rx="1.5" fill="white"/>
            <rect x="13" y="4" width="7" height="7" rx="1.5" fill="white" opacity="0.7"/>
            <rect x="4" y="13" width="7" height="7" rx="1.5" fill="white" opacity="0.7"/>
            <rect x="13" y="13" width="7" height="7" rx="1.5" fill="white" opacity="0.5"/>
          </svg>
          <span>ProtoFlow</span>
          <span class="preview-badge">预览</span>
        </div>
        <div class="preview-title">{{ project.title || '原型预览' }}</div>
        <!-- Page selector -->
        <div class="page-tabs" v-if="project.pages.length > 1">
          <button v-for="page in project.pages" :key="page.id" :class="{ active: currentPageIdx === project.pages.indexOf(page) }" @click="currentPageIdx = project.pages.indexOf(page)">{{ page.name }}</button>
        </div>
        <div class="preview-toolbar-right">
          <div class="device-switcher">
            <button :class="{ active: device === 'desktop' }" @click="device = 'desktop'" title="桌面端">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            </button>
            <button :class="{ active: device === 'tablet' }" @click="device = 'tablet'" title="平板端">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><circle cx="12" cy="18" r="1"/></svg>
            </button>
            <button :class="{ active: device === 'mobile' }" @click="device = 'mobile'" title="移动端">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><circle cx="12" cy="17" r="1"/></svg>
            </button>
          </div>
          <label class="annotation-toggle">
            <input type="checkbox" v-model="showAnnotations" />
            <span>标注</span>
          </label>
          <button class="zoom-ctrl" @click="previewZoom = Math.max(0.3, previewZoom - 0.1)">−</button>
          <span class="zoom-val">{{ Math.round(previewZoom * 100) }}%</span>
          <button class="zoom-ctrl" @click="previewZoom = Math.min(3, previewZoom + 0.1)">+</button>
          <button class="zoom-ctrl" @click="previewZoom = 1">⊙</button>
        </div>
      </div>

      <!-- Preview Canvas Area -->
      <div class="preview-area" :class="`device-${device}`">
        <div class="preview-device-frame" v-if="device !== 'desktop'">
          <div class="device-screen">
            <div class="preview-canvas-scroll">
              <div class="preview-canvas" :style="canvasStyle">
                <PreviewElement v-for="el in currentPageElements" :key="el.id" :element="el" :showAnnotations="showAnnotations" />
              </div>
            </div>
          </div>
        </div>
        <div v-else class="preview-canvas-scroll">
          <div class="preview-canvas" :style="canvasStyle">
            <PreviewElement v-for="el in currentPageElements" :key="el.id" :element="el" :showAnnotations="showAnnotations" />
          </div>
        </div>
      </div>

      <!-- Bottom Info Bar -->
      <div class="preview-bottom-bar">
        <span>{{ project.pages.length }} 个页面 · {{ totalElements }} 个元素</span>
        <span>由 ProtoFlow 创建</span>
        <span class="share-time">{{ formatDate(project.createdAt) }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { loadSharedProject } from '../store/editorStore.js'
import PreviewElement from '../components/canvas/PreviewElement.vue'

const loading = ref(true)
const error = ref(false)
const project = ref(null)
const currentPageIdx = ref(0)
const device = ref('desktop')
const previewZoom = ref(1)
const showAnnotations = ref(false)

const currentPage = computed(() => project.value?.pages[currentPageIdx.value])
const currentPageElements = computed(() => {
  return [...(currentPage.value?.elements || [])].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
})
const totalElements = computed(() => project.value?.pages.reduce((sum, p) => sum + (p.elements?.length || 0), 0) || 0)

const canvasStyle = computed(() => ({
  width: (currentPage.value?.width || 1440) + 'px',
  height: (currentPage.value?.height || 900) + 'px',
  background: currentPage.value?.background || '#ffffff',
  transform: `scale(${previewZoom.value})`,
  transformOrigin: 'top left',
  position: 'relative',
  overflow: 'hidden',
}))

function goBack() { window.location.hash = '/' }

function formatDate(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

onMounted(() => {
  const hash = window.location.hash
  const match = hash.match(/\/preview\/([a-zA-Z0-9]+)/)
  if (match) {
    const shareId = match[1]
    setTimeout(() => {
      const data = loadSharedProject(shareId)
      if (data) {
        project.value = data
        loading.value = false
      } else {
        error.value = true
        loading.value = false
      }
    }, 600)
  } else {
    error.value = true
    loading.value = false
  }
})
</script>

<style scoped>
.preview-app { width: 100vw; height: 100vh; display: flex; flex-direction: column; background: #0f0f1a; font-family: 'Inter', sans-serif; overflow: hidden; }
.preview-loading, .preview-error { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; color: #9ca3af; }
.loading-spinner { width: 40px; height: 40px; border: 3px solid #2a2a3e; border-top-color: #4F8EF7; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-icon { font-size: 48px; }
.preview-error h2 { color: #e0e0f0; font-size: 20px; margin: 0; }
.preview-error p { color: #6b7280; font-size: 14px; text-align: center; max-width: 320px; margin: 0; }
.preview-error button { padding: 10px 24px; background: #4F8EF7; border: none; border-radius: 8px; color: #fff; font-size: 14px; cursor: pointer; }
.preview-toolbar { height: 52px; background: #12121e; border-bottom: 1px solid #1e1e30; display: flex; align-items: center; padding: 0 16px; gap: 12px; flex-shrink: 0; }
.preview-logo { display: flex; align-items: center; gap: 8px; color: #e0e0f0; font-size: 14px; font-weight: 700; }
.preview-badge { background: #4F8EF7; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px; font-weight: 600; }
.preview-title { color: #9ca3af; font-size: 13px; margin-left: 8px; }
.page-tabs { display: flex; gap: 4px; background: #1e1e30; border-radius: 8px; padding: 3px; }
.page-tabs button { padding: 4px 12px; border: none; background: none; color: #9ca3af; border-radius: 6px; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.page-tabs button.active { background: #4F8EF7; color: #fff; }
.preview-toolbar-right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
.device-switcher { display: flex; gap: 3px; background: #1e1e30; border-radius: 8px; padding: 3px; }
.device-switcher button { width: 28px; height: 28px; border: none; background: none; color: #9ca3af; border-radius: 5px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.device-switcher button.active { background: #4F8EF7; color: #fff; }
.annotation-toggle { display: flex; align-items: center; gap: 6px; color: #9ca3af; font-size: 12px; cursor: pointer; }
.annotation-toggle input { accent-color: #4F8EF7; }
.zoom-ctrl { width: 28px; height: 28px; border: 1px solid #2a2a3e; background: #1e1e30; color: #9ca3af; border-radius: 6px; cursor: pointer; font-size: 16px; transition: all 0.1s; }
.zoom-ctrl:hover { border-color: #4F8EF7; color: #4F8EF7; }
.zoom-val { color: #9ca3af; font-size: 12px; min-width: 36px; text-align: center; }
.preview-area { flex: 1; overflow: auto; display: flex; align-items: flex-start; justify-content: center; padding: 24px; }
.preview-canvas-scroll { overflow: auto; }
.preview-canvas { box-shadow: 0 8px 48px rgba(0,0,0,0.4); }
.device-mobile .preview-canvas-scroll, .device-tablet .preview-canvas-scroll { overflow: hidden; }
.preview-device-frame { background: #1e1e30; border-radius: 24px; padding: 12px; box-shadow: 0 8px 40px rgba(0,0,0,0.5); }
.device-screen { overflow: hidden; border-radius: 12px; }
.device-mobile .device-screen { width: 390px; height: 844px; }
.device-tablet .device-screen { width: 768px; height: 1024px; }
.preview-bottom-bar { height: 32px; background: #12121e; border-top: 1px solid #1e1e30; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; color: #4a4a6a; font-size: 11px; flex-shrink: 0; }
</style>
