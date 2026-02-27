<template>
  <div class="el-wrapper" :style="wrapperStyle" :class="{ selected, locked: element.locked, 'editing': editing }" @mousedown="$emit('mousedown', $event)" @dblclick="$emit('dblclick', $event)">
    <!-- Text element -->
    <div v-if="element.type === 'text'" class="el-text" :style="textStyle">
      <div v-if="!editing" class="el-text-content" v-html="formattedText"></div>
      <div v-else contenteditable="true" class="el-text-edit" :style="textStyle" @input="onTextInput" @blur="onTextBlur" @keydown.stop @mousedown.stop ref="textEditRef">{{ element.text }}</div>
    </div>
    <!-- Button element -->
    <div v-else-if="element.type === 'button'" class="el-button" :style="buttonStyle">
      <span v-if="!editing">{{ element.text || '按钮' }}</span>
      <span v-else contenteditable="true" @input="onTextInput" @blur="onTextBlur" @keydown.stop @mousedown.stop ref="textEditRef">{{ element.text }}</span>
    </div>
    <!-- Input element -->
    <div v-else-if="element.type === 'input'" class="el-input" :style="inputStyle">
      <span class="el-input-placeholder">{{ element.placeholder || '请输入内容...' }}</span>
    </div>
    <!-- Navbar element -->
    <div v-else-if="element.type === 'navbar'" class="el-navbar" :style="navbarStyle">
      <div class="navbar-left">☰</div>
      <span v-if="!editing">{{ element.text || 'Navigation' }}</span>
      <span v-else contenteditable="true" @input="onTextInput" @blur="onTextBlur" @keydown.stop @mousedown.stop ref="textEditRef">{{ element.text }}</span>
      <div class="navbar-right">···</div>
    </div>
    <!-- Rectangle element -->
    <div v-else-if="element.type === 'rectangle'" class="el-rect" :style="rectStyle"></div>
    <!-- Card element -->
    <div v-else-if="element.type === 'card'" class="el-card" :style="cardStyle">
      <div class="card-header" :style="{ background: element.fill || '#fff' }"></div>
      <div class="card-content">
        <div class="card-line"></div>
        <div class="card-line short"></div>
      </div>
    </div>
    <!-- Circle element -->
    <svg v-else-if="element.type === 'circle'" :width="element.width" :height="element.height">
      <ellipse :cx="element.width/2" :cy="element.height/2" :rx="element.width/2 - (element.strokeWidth||0)/2" :ry="element.height/2 - (element.strokeWidth||0)/2" :fill="element.fill || '#4F8EF7'" :stroke="element.stroke || 'transparent'" :stroke-width="element.strokeWidth || 0" :opacity="(element.opacity||100)/100" />
    </svg>
    <!-- Triangle element -->
    <svg v-else-if="element.type === 'triangle'" :width="element.width" :height="element.height">
      <polygon :points="`${element.width/2},0 ${element.width},${element.height} 0,${element.height}`" :fill="element.fill || '#10b981'" :stroke="element.stroke || 'transparent'" :stroke-width="element.strokeWidth || 0" />
    </svg>
    <!-- Divider element -->
    <div v-else-if="element.type === 'divider'" class="el-divider" :style="dividerStyle"></div>
    <!-- Icon element -->
    <div v-else-if="element.type === 'icon'" class="el-icon" :style="iconStyle">
      <svg :width="element.width * 0.6" :height="element.height * 0.6" viewBox="0 0 24 24" :fill="element.fill || '#4F8EF7'">
        <path v-if="element.iconType === 'star'" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        <path v-else-if="element.iconType === 'heart'" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        <circle v-else cx="12" cy="12" r="10"/>
      </svg>
    </div>
    <!-- Image element -->
    <div v-else-if="element.type === 'image'" class="el-image" :style="imageStyle">
      <img v-if="element.src" :src="element.src" :style="{ width:'100%', height:'100%', objectFit:'cover', borderRadius: (element.borderRadius||0)+'px' }" />
      <div v-else class="el-image-placeholder">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="#9ca3af"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
        <span>图片</span>
      </div>
    </div>
    <!-- Fallback -->
    <div v-else class="el-fallback" :style="rectStyle"></div>

    <!-- Visibility toggle if hidden -->
    <div v-if="!element.visible" class="el-hidden-overlay">隐藏</div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'

const props = defineProps({ element: Object, selected: Boolean, editing: Boolean, zoom: Number })
const emit = defineEmits(['mousedown', 'dblclick', 'update', 'endEdit'])
const textEditRef = ref(null)

watch(() => props.editing, (val) => {
  if (val) nextTick(() => textEditRef.value?.focus())
})

const wrapperStyle = computed(() => ({
  position: 'absolute',
  left: props.element.x + 'px',
  top: props.element.y + 'px',
  width: props.element.width + 'px',
  height: props.element.height + 'px',
  opacity: (props.element.opacity ?? 100) / 100,
  transform: props.element.rotation ? `rotate(${props.element.rotation}deg)` : undefined,
  cursor: props.element.locked ? 'not-allowed' : 'move',
  zIndex: props.element.zIndex || 0,
  display: props.element.visible === false ? 'none' : undefined,
  pointerEvents: props.element.locked ? 'none' : 'all',
}))

const baseBoxStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || 'transparent',
  border: props.element.strokeWidth ? `${props.element.strokeWidth}px solid ${props.element.stroke || 'transparent'}` : 'none',
  borderRadius: (props.element.borderRadius || 0) + 'px',
  boxSizing: 'border-box',
  boxShadow: props.element.shadow ? '0 4px 24px rgba(0,0,0,0.12)' : 'none',
}))

const textStyle = computed(() => ({
  width: '100%',
  height: '100%',
  color: props.element.color || '#1a1a2e',
  fontSize: (props.element.fontSize || 16) + 'px',
  fontFamily: props.element.fontFamily || 'Inter, sans-serif',
  fontWeight: props.element.fontWeight || 'normal',
  fontStyle: props.element.fontStyle || 'normal',
  textDecoration: props.element.textDecoration || 'none',
  textAlign: props.element.textAlign || 'left',
  lineHeight: props.element.lineHeight || 1.5,
  padding: '4px',
  boxSizing: 'border-box',
  overflow: 'hidden',
  background: 'transparent',
  border: 'none',
  outline: 'none',
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
}))

const rectStyle = computed(() => ({
  ...baseBoxStyle.value,
  backgroundImage: props.element.gradient || undefined,
}))

const cardStyle = computed(() => ({
  ...baseBoxStyle.value,
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
}))

const buttonStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#4F8EF7',
  border: props.element.strokeWidth ? `${props.element.strokeWidth}px solid ${props.element.stroke}` : 'none',
  borderRadius: (props.element.borderRadius || 8) + 'px',
  color: props.element.color || '#ffffff',
  fontSize: (props.element.fontSize || 14) + 'px',
  fontFamily: props.element.fontFamily || 'Inter, sans-serif',
  fontWeight: props.element.fontWeight || '600',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  boxSizing: 'border-box',
  letterSpacing: '0.02em',
}))

const inputStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#ffffff',
  border: `${props.element.strokeWidth || 1.5}px solid ${props.element.stroke || '#d1d5db'}`,
  borderRadius: (props.element.borderRadius || 8) + 'px',
  display: 'flex',
  alignItems: 'center',
  padding: '0 12px',
  boxSizing: 'border-box',
  gap: '8px',
}))

const navbarStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#ffffff',
  borderBottom: `${props.element.strokeWidth || 1}px solid ${props.element.stroke || '#e5e7eb'}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '0 16px',
  boxSizing: 'border-box',
  color: props.element.color || '#1a1a2e',
  fontSize: (props.element.fontSize || 16) + 'px',
  fontWeight: props.element.fontWeight || '600',
  fontFamily: props.element.fontFamily || 'Inter, sans-serif',
}))

const dividerStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#e5e7eb',
  borderRadius: (props.element.borderRadius || 0) + 'px',
}))

const iconStyle = computed(() => ({
  width: '100%',
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

const imageStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#f3f4f6',
  border: `${props.element.strokeWidth || 1}px solid ${props.element.stroke || '#e5e7eb'}`,
  borderRadius: (props.element.borderRadius || 4) + 'px',
  overflow: 'hidden',
  boxSizing: 'border-box',
}))

const formattedText = computed(() => {
  return (props.element.text || '').replace(/\n/g, '<br>')
})

function onTextInput(e) {
  emit('update', { text: e.target.innerText || e.target.textContent })
}
function onTextBlur() {
  emit('endEdit')
}
</script>

<style scoped>
.el-wrapper { user-select: none; }
.el-wrapper.selected { outline: 2px solid #4F8EF7; outline-offset: 1px; }
.el-text { display: flex; flex-direction: column; justify-content: flex-start; }
.el-text-content { width: 100%; height: 100%; white-space: pre-wrap; word-break: break-word; }
.el-text-edit { width: 100%; min-height: 100%; outline: none; white-space: pre-wrap; word-break: break-word; caret-color: #4F8EF7; }
.el-input-placeholder { color: #9ca3af; font-size: 14px; font-family: Inter, sans-serif; user-select: none; }
.card-header { height: 48%; flex-shrink: 0; }
.card-content { flex: 1; padding: 10px 14px; display: flex; flex-direction: column; gap: 8px; background: #fff; }
.card-line { height: 10px; background: #e5e7eb; border-radius: 4px; }
.card-line.short { width: 60%; }
.el-image { position: relative; }
.el-image-placeholder { width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; color:#9ca3af; font-size:12px; }
.el-hidden-overlay { position:absolute; inset:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; color:#fff; font-size:12px; border-radius:inherit; }
.navbar-left, .navbar-right { font-size: 18px; color: #6b7280; cursor: pointer; }
</style>
