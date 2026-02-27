<template>
  <header class="toolbar" @keydown.stop @keyup.stop>
    <!-- Logo -->
    <div class="toolbar-logo">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#4F8EF7"/>
        <rect x="4" y="4" width="7" height="7" rx="1.5" fill="white"/>
        <rect x="13" y="4" width="7" height="7" rx="1.5" fill="white" opacity="0.7"/>
        <rect x="4" y="13" width="7" height="7" rx="1.5" fill="white" opacity="0.7"/>
        <rect x="13" y="13" width="7" height="7" rx="1.5" fill="white" opacity="0.5"/>
      </svg>
      <span class="logo-text">ProtoFlow</span>
    </div>

    <!-- Title (editable) -->
    <div class="toolbar-title">
      <input class="title-input" v-model="projectTitle" placeholder="未命名原型" />
    </div>

    <!-- Tools -->
    <div class="toolbar-tools">
      <button class="tool-btn" :class="{ active: store.tool === 'select' }" @click="store.tool = 'select'" title="选择工具 (V)">
        <svg width="16" height="16" viewBox="0 0 16 16"><path d="M2 2l4.5 11.5 2.5-3.5 4 1-11-9z" fill="currentColor"/></svg>
      </button>
      <div class="tool-separator"></div>
      <!-- Undo/Redo -->
      <button class="tool-btn" @click="undo" title="撤销 (⌘Z)" :disabled="store.historyIndex <= 0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg>
      </button>
      <button class="tool-btn" @click="redo" title="重做 (⌘⇧Z)" :disabled="store.historyIndex >= store.history.length - 1">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 14 20 9 15 4"/><path d="M4 20v-7a4 4 0 0 1 4-4h12"/></svg>
      </button>
      <div class="tool-separator"></div>
      <!-- Grid toggle -->
      <button class="tool-btn" :class="{ active: store.showGrid }" @click="store.showGrid = !store.showGrid" title="网格">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="5" height="5" rx="0.5" stroke="currentColor" stroke-width="1.2"/><rect x="10" y="1" width="5" height="5" rx="0.5" stroke="currentColor" stroke-width="1.2"/><rect x="1" y="10" width="5" height="5" rx="0.5" stroke="currentColor" stroke-width="1.2"/><rect x="10" y="10" width="5" height="5" rx="0.5" stroke="currentColor" stroke-width="1.2"/></svg>
      </button>
      <button class="tool-btn" :class="{ active: store.snapToGrid }" @click="store.snapToGrid = !store.snapToGrid" title="对齐网格">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20"/><circle cx="12" cy="12" r="3"/></svg>
      </button>
    </div>

    <!-- Spacer -->
    <div class="flex-1"></div>

    <!-- Right actions -->
    <div class="toolbar-actions">
      <button class="action-btn preview-btn" @click="openPreview" title="预览原型">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        预览
      </button>
      <button class="action-btn share-btn" @click="showShareModal = true">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        分享
      </button>
    </div>

    <!-- Share Modal -->
    <Teleport to="body">
      <div v-if="showShareModal" class="modal-overlay" @click.self="showShareModal = false">
        <div class="modal">
          <div class="modal-header">
            <div class="modal-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4F8EF7" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
              分享原型
            </div>
            <button class="modal-close" @click="showShareModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="share-info">
              <p>生成分享链接后，开发团队可以直接在浏览器中访问你的高保真原型，无需安装任何软件。</p>
            </div>
            <div v-if="!shareLink" class="share-generate">
              <div class="share-options">
                <label class="share-option">
                  <input type="checkbox" v-model="shareCanInteract" />
                  <span>允许交互（点击、滚动）</span>
                </label>
                <label class="share-option">
                  <input type="checkbox" v-model="shareShowDimensions" />
                  <span>显示元素尺寸标注</span>
                </label>
              </div>
              <button class="generate-btn" @click="generateLink">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                生成分享链接
              </button>
            </div>
            <div v-else class="share-result">
              <div class="share-success-icon">✅</div>
              <p class="share-success-text">链接已生成！将链接发给开发团队，他们可以直接浏览原型。</p>
              <div class="link-box">
                <input class="link-input" :value="shareLink" readonly ref="linkInputRef" />
                <button class="copy-btn" @click="copyLink" :class="{ copied: justCopied }">{{ justCopied ? '✓ 已复制' : '复制' }}</button>
              </div>
              <div class="share-meta">
                <span>📄 {{ store.pages.length }} 个页面</span>
                <span>🧩 {{ totalElements }} 个元素</span>
                <span>🕐 有效期：永久</span>
              </div>
              <div class="share-actions-row">
                <button class="open-link-btn" @click="openShareLink">在新标签页打开</button>
                <button class="regenerate-btn" @click="shareLink = ''; justCopied = false">重新生成</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { store, undo, redo, generateShareLink } from '../../store/editorStore.js'

const showShareModal = ref(false)
const shareLink = ref('')
const justCopied = ref(false)
const linkInputRef = ref(null)
const projectTitle = ref('未命名原型')
const shareCanInteract = ref(true)
const shareShowDimensions = ref(false)

const totalElements = computed(() => store.pages.reduce((sum, p) => sum + (p.elements?.length || 0), 0))

function generateLink() {
  shareLink.value = generateShareLink()
}

function copyLink() {
  linkInputRef.value?.select()
  navigator.clipboard.writeText(shareLink.value).then(() => {
    justCopied.value = true
    setTimeout(() => { justCopied.value = false }, 2000)
  }).catch(() => {
    document.execCommand('copy')
    justCopied.value = true
    setTimeout(() => { justCopied.value = false }, 2000)
  })
}

function openShareLink() {
  window.open(shareLink.value, '_blank')
}

function openPreview() {
  const link = generateShareLink()
  window.open(link, '_blank')
}
</script>

<style scoped>
.toolbar {
  height: 52px;
  background: #12121e;
  border-bottom: 1px solid #1e1e30;
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 8px;
  flex-shrink: 0;
  z-index: 100;
  user-select: none;
}
.toolbar-logo { display: flex; align-items: center; gap: 8px; margin-right: 8px; }
.logo-text { font-size: 15px; font-weight: 700; color: #e0e0f0; font-family: 'Inter', sans-serif; letter-spacing: -0.02em; }
.toolbar-title { margin: 0 8px; }
.title-input { background: transparent; border: 1px solid transparent; color: #c0c0d8; font-size: 13px; font-family: 'Inter', sans-serif; padding: 4px 8px; border-radius: 6px; outline: none; width: 160px; transition: all 0.15s; }
.title-input:hover, .title-input:focus { border-color: #2a2a3e; background: #1e1e30; color: #e0e0f0; }
.toolbar-tools { display: flex; align-items: center; gap: 4px; }
.tool-btn { width: 32px; height: 32px; border: 1px solid transparent; background: none; color: #7a7a9a; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.tool-btn:hover { background: #1e1e30; color: #c0c0d8; border-color: #2a2a3e; }
.tool-btn.active { background: #1e2a4a; color: #4F8EF7; border-color: #4F8EF7; }
.tool-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.tool-separator { width: 1px; height: 20px; background: #2a2a3e; margin: 0 4px; }
.flex-1 { flex: 1; }
.toolbar-actions { display: flex; align-items: center; gap: 8px; }
.action-btn { display: flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 8px; font-size: 13px; font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer; border: none; transition: all 0.15s; }
.preview-btn { background: #1e2a4a; color: #4F8EF7; border: 1px solid #2a3a5e; }
.preview-btn:hover { background: #253460; border-color: #4F8EF7; }
.share-btn { background: linear-gradient(135deg, #4F8EF7 0%, #7c3aed 100%); color: #fff; }
.share-btn:hover { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(79,142,247,0.4); }
/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 10000; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px); }
.modal { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 16px; width: 480px; max-width: 95vw; box-shadow: 0 20px 60px rgba(0,0,0,0.5); overflow: hidden; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 0; }
.modal-title { display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 700; color: #e0e0f0; font-family: 'Inter', sans-serif; }
.modal-close { background: none; border: none; color: #6b7280; font-size: 22px; cursor: pointer; padding: 0; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 6px; transition: all 0.1s; }
.modal-close:hover { background: #2a2a3e; color: #e0e0f0; }
.modal-body { padding: 20px 24px 24px; }
.share-info p { color: #9ca3af; font-size: 13px; line-height: 1.6; margin: 0 0 16px; }
.share-options { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.share-option { display: flex; align-items: center; gap: 8px; color: #c0c0d8; font-size: 13px; cursor: pointer; }
.share-option input { accent-color: #4F8EF7; width: 14px; height: 14px; }
.generate-btn { width: 100%; padding: 12px; background: linear-gradient(135deg, #4F8EF7 0%, #7c3aed 100%); border: none; border-radius: 10px; color: #fff; font-size: 14px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.15s; font-family: 'Inter', sans-serif; }
.generate-btn:hover { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 6px 20px rgba(79,142,247,0.4); }
.share-success-icon { font-size: 32px; text-align: center; margin-bottom: 8px; }
.share-success-text { color: #6ee7b7; font-size: 13px; text-align: center; margin: 0 0 14px; }
.link-box { display: flex; gap: 8px; margin-bottom: 12px; }
.link-input { flex: 1; background: #12121e; border: 1px solid #2a2a3e; color: #e0e0f0; border-radius: 8px; padding: 9px 12px; font-size: 12px; outline: none; font-family: monospace; }
.copy-btn { padding: 9px 16px; background: #1e2a4a; border: 1px solid #2a3a5e; color: #4F8EF7; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; white-space: nowrap; transition: all 0.15s; }
.copy-btn.copied { background: #1a3a2a; border-color: #10b981; color: #10b981; }
.copy-btn:hover:not(.copied) { background: #253460; }
.share-meta { display: flex; gap: 12px; justify-content: center; font-size: 12px; color: #6b7280; margin-bottom: 14px; flex-wrap: wrap; }
.share-actions-row { display: flex; gap: 8px; }
.open-link-btn { flex: 1; padding: 9px; background: #1e1e30; border: 1px solid #2a2a3e; color: #c0c0d8; border-radius: 8px; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.open-link-btn:hover { border-color: #4F8EF7; color: #4F8EF7; }
.regenerate-btn { padding: 9px 14px; background: none; border: 1px solid #2a2a3e; color: #6b7280; border-radius: 8px; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.regenerate-btn:hover { border-color: #6b7280; color: #9ca3af; }
</style>
