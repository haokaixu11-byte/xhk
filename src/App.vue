<template>
  <div id="app">
    <!-- Preview Mode (from shared link) -->
    <PreviewView v-if="isPreview" />
    <!-- Editor Mode -->
    <div v-else class="editor-layout">
      <TopToolbar />
      <div class="editor-body">
        <LeftPanel />
        <main class="canvas-area" @dragover.prevent @drop="onDrop">
          <CanvasStage />
        </main>
        <RightPanel />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import TopToolbar from './components/toolbar/TopToolbar.vue'
import LeftPanel from './components/panels/LeftPanel.vue'
import RightPanel from './components/panels/RightPanel.vue'
import CanvasStage from './components/canvas/CanvasStage.vue'
import PreviewView from './views/PreviewView.vue'
import { addElement } from './store/editorStore.js'

const isPreview = ref(false)

function checkRoute() {
  isPreview.value = window.location.hash.startsWith('#/preview/')
}

onMounted(() => {
  checkRoute()
  window.addEventListener('hashchange', checkRoute)
})

function onDrop(e) {
  const type = e.dataTransfer.getData('comp_type')
  if (type) {
    const rect = e.currentTarget.getBoundingClientRect()
    addElement(type, e.clientX - rect.left - 60, e.clientY - rect.top - 20)
  }
}
</script>

<style>

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; overflow: hidden; }
#app { width: 100vw; height: 100vh; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

.editor-layout {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  background: #0f0f1a;
  overflow: hidden;
}

.editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.canvas-area {
  flex: 1;
  overflow: hidden;
  position: relative;
  min-width: 0;
}

/* Scrollbar styling */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #12121e; }
::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a5a; }

/* Input number arrows hide */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button { opacity: 0.5; }
</style>
