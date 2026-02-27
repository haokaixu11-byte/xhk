<template>
  <div class="pv-el" :style="wrapperStyle" :class="{ 'show-ann': showAnnotations }" @mouseenter="hovering = true" @mouseleave="hovering = false">
    <!-- Annotation tooltip -->
    <div v-if="showAnnotations && hovering" class="ann-tooltip">
      <div class="ann-row"><span>{{ element.name }}</span></div>
      <div class="ann-row"><span class="ann-label">W</span><span>{{ element.width }}px</span><span class="ann-label">H</span><span>{{ element.height }}px</span></div>
      <div class="ann-row"><span class="ann-label">X</span><span>{{ element.x }}px</span><span class="ann-label">Y</span><span>{{ element.y }}px</span></div>
      <div v-if="element.fill && element.fill !== 'transparent'" class="ann-row"><span class="ann-label">Fill</span><span class="ann-color" :style="{ background: element.fill }"></span><span>{{ element.fill }}</span></div>
      <div v-if="element.fontSize" class="ann-row"><span class="ann-label">Font</span><span>{{ element.fontSize }}px {{ element.fontWeight || '' }}</span></div>
    </div>

    <!-- Render elements same as editor but without interaction -->
    <div v-if="element.type === 'text'" :style="textStyle" class="pv-text" v-html="formattedText"></div>
    <div v-else-if="element.type === 'button'" :style="buttonStyle" class="pv-button">{{ element.text || '按钮' }}</div>
    <div v-else-if="element.type === 'input'" :style="inputStyle" class="pv-input"><span style="color:#9ca3af;font-size:14px">{{ element.placeholder || '请输入内容...' }}</span></div>
    <div v-else-if="element.type === 'navbar'" :style="navbarStyle" class="pv-navbar">
      <span style="font-size:18px;color:#6b7280">☰</span>
      <span>{{ element.text || 'Navigation' }}</span>
      <span style="font-size:18px;color:#6b7280">···</span>
    </div>
    <div v-else-if="element.type === 'rectangle'" :style="rectStyle"></div>
    <div v-else-if="element.type === 'card'" :style="cardStyle" class="pv-card">
      <div class="card-header-img" :style="{ background: element.fill || '#4F8EF7', height: '45%' }"></div>
      <div class="card-body">
        <div class="card-line"></div>
        <div class="card-line short"></div>
      </div>
    </div>
    <svg v-else-if="element.type === 'circle'" :width="element.width" :height="element.height" style="overflow:visible">
      <ellipse :cx="element.width/2" :cy="element.height/2" :rx="element.width/2 - (element.strokeWidth||0)/2" :ry="element.height/2 - (element.strokeWidth||0)/2" :fill="element.fill || '#4F8EF7'" :stroke="element.stroke || 'transparent'" :stroke-width="element.strokeWidth || 0" />
    </svg>
    <svg v-else-if="element.type === 'triangle'" :width="element.width" :height="element.height">
      <polygon :points="`${element.width/2},0 ${element.width},${element.height} 0,${element.height}`" :fill="element.fill || '#10b981'" />
    </svg>
    <div v-else-if="element.type === 'divider'" :style="dividerStyle"></div>
    <div v-else-if="element.type === 'icon'" :style="iconStyle" class="pv-icon">
      <svg :width="element.width * 0.6" :height="element.height * 0.6" viewBox="0 0 24 24" :fill="element.fill || '#4F8EF7'">
        <path v-if="element.iconType === 'star'" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        <path v-else-if="element.iconType === 'heart'" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        <circle v-else cx="12" cy="12" r="10"/>
      </svg>
    </div>
    <div v-else-if="element.type === 'image'" :style="imageStyle" class="pv-image">
      <img v-if="element.src" :src="element.src" style="width:100%;height:100%;object-fit:cover" />
      <div v-else class="pv-img-placeholder">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="#9ca3af"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
      </div>
    </div>
    <div v-else :style="rectStyle"></div>

    <!-- Annotation size overlay -->
    <div v-if="showAnnotations" class="ann-size-overlay">
      <span class="ann-w">{{ element.width }}</span>
      <span class="ann-h">{{ element.height }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ element: Object, showAnnotations: Boolean })
const hovering = ref(false)

const wrapperStyle = computed(() => ({
  position: 'absolute',
  left: props.element.x + 'px',
  top: props.element.y + 'px',
  width: props.element.width + 'px',
  height: props.element.height + 'px',
  opacity: (props.element.opacity ?? 100) / 100,
  transform: props.element.rotation ? `rotate(${props.element.rotation}deg)` : undefined,
  zIndex: props.element.zIndex || 0,
  display: props.element.visible === false ? 'none' : undefined,
}))
const rectStyle = computed(() => ({ width: '100%', height: '100%', background: props.element.fill || 'transparent', border: props.element.strokeWidth ? `${props.element.strokeWidth}px solid ${props.element.stroke}` : 'none', borderRadius: (props.element.borderRadius || 0) + 'px', boxSizing: 'border-box', boxShadow: props.element.shadow ? '0 4px 24px rgba(0,0,0,0.12)' : 'none' }))
const textStyle = computed(() => ({ width: '100%', height: '100%', color: props.element.color || '#1a1a2e', fontSize: (props.element.fontSize || 16) + 'px', fontFamily: props.element.fontFamily || 'Inter, sans-serif', fontWeight: props.element.fontWeight || 'normal', fontStyle: props.element.fontStyle || 'normal', textDecoration: props.element.textDecoration || 'none', textAlign: props.element.textAlign || 'left', lineHeight: props.element.lineHeight || 1.5, padding: '4px', boxSizing: 'border-box', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }))
const buttonStyle = computed(() => ({ width: '100%', height: '100%', background: props.element.fill || '#4F8EF7', border: 'none', borderRadius: (props.element.borderRadius || 8) + 'px', color: props.element.color || '#fff', fontSize: (props.element.fontSize || 14) + 'px', fontWeight: props.element.fontWeight || '600', display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box', fontFamily: props.element.fontFamily || 'Inter, sans-serif', cursor: 'pointer' }))
const inputStyle = computed(() => ({ width: '100%', height: '100%', background: props.element.fill || '#fff', border: `${props.element.strokeWidth || 1.5}px solid ${props.element.stroke || '#d1d5db'}`, borderRadius: (props.element.borderRadius || 8) + 'px', display: 'flex', alignItems: 'center', padding: '0 12px', boxSizing: 'border-box' }))
const navbarStyle = computed(() => ({ width: '100%', height: '100%', background: props.element.fill || '#fff', borderBottom: `1px solid ${props.element.stroke || '#e5e7eb'}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', boxSizing: 'border-box', color: props.element.color || '#1a1a2e', fontSize: (props.element.fontSize || 16) + 'px', fontWeight: props.element.fontWeight || '600' }))
const cardStyle = computed(() => ({ width: '100%', height: '100%', background: '#fff', border: `1px solid ${props.element.stroke || '#e5e7eb'}`, borderRadius: (props.element.borderRadius || 12) + 'px', overflow: 'hidden', boxSizing: 'border-box', boxShadow: props.element.shadow ? '0 4px 24px rgba(0,0,0,0.12)' : 'none', display: 'flex', flexDirection: 'column' }))
const dividerStyle = computed(() => ({ width: '100%', height: '100%', background: props.element.fill || '#e5e7eb' }))
const iconStyle = computed(() => ({ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }))
const imageStyle = computed(() => ({ width: '100%', height: '100%', background: props.element.fill || '#f3f4f6', border: `1px solid ${props.element.stroke || '#e5e7eb'}`, borderRadius: (props.element.borderRadius || 4) + 'px', overflow: 'hidden', boxSizing: 'border-box' }))
const formattedText = computed(() => (props.element.text || '').replace(/\n/g, '<br>'))
</script>

<style scoped>
.pv-el { cursor: default; }
.pv-text { overflow: hidden; }
.pv-button { cursor: pointer; }
.pv-button:hover { filter: brightness(0.92); }
.pv-input { cursor: text; }
.pv-icon { display: flex; align-items: center; justify-content: center; }
.pv-image { overflow: hidden; }
.pv-img-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.card-header-img { flex-shrink: 0; }
.card-body { flex: 1; padding: 10px 14px; background: #fff; display: flex; flex-direction: column; gap: 8px; }
.card-line { height: 10px; background: #e5e7eb; border-radius: 4px; }
.card-line.short { width: 60%; }
/* Annotations */
.ann-tooltip { position: absolute; bottom: calc(100% + 8px); left: 0; background: rgba(20,20,40,0.95); border: 1px solid #2a2a3e; border-radius: 8px; padding: 8px 10px; z-index: 99999; min-width: 160px; pointer-events: none; display: flex; flex-direction: column; gap: 4px; backdrop-filter: blur(8px); }
.ann-row { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #e0e0f0; font-family: monospace; }
.ann-label { color: #6b7280; min-width: 28px; }
.ann-color { width: 12px; height: 12px; border-radius: 2px; border: 1px solid rgba(255,255,255,0.15); flex-shrink: 0; }
.ann-size-overlay { position: absolute; inset: 0; pointer-events: none; }
.ann-w { position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: 10px; background: #4F8EF7; color: #fff; padding: 1px 5px; border-radius: 3px; white-space: nowrap; font-family: monospace; }
.ann-h { position: absolute; top: 50%; right: -30px; transform: translateY(-50%); font-size: 10px; background: #4F8EF7; color: #fff; padding: 1px 5px; border-radius: 3px; white-space: nowrap; font-family: monospace; }
.pv-el.show-ann { outline: 1px dashed rgba(79,142,247,0.3); }
.pv-el.show-ann:hover { outline: 2px solid #4F8EF7; }
</style>
