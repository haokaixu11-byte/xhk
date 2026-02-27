<template>
  <div
    class="el-wrapper"
    :style="wrapperStyle"
    :class="{ selected, locked: element.locked }"
    @mousedown="onWrapperMousedown"
    @dblclick.stop="onWrapperDblClick"
  >
    <!-- ===== TEXT ===== -->
    <div v-if="element.type === 'text'" class="el-text" :style="textStyle">
      <div
        v-if="!editing"
        class="el-text-display"
        v-html="formattedText"
      ></div>
      <textarea
        v-if="editing"
        ref="textareaRef"
        class="el-textarea"
        :style="textareaStyle"
        v-model="localText"
        @blur="commitText"
        @keydown.stop
        @mousedown.stop
        @click.stop
      ></textarea>
    </div>

    <!-- ===== BUTTON ===== -->
    <div v-else-if="element.type === 'button'" class="el-button" :style="buttonStyle">
      <span v-if="!editing" class="el-button-label">{{ element.text || '按钮' }}</span>
      <textarea
        v-if="editing"
        ref="textareaRef"
        class="el-textarea-inline"
        :style="textareaInlineStyle"
        v-model="localText"
        @blur="commitText"
        @keydown.stop
        @mousedown.stop
        @click.stop
      ></textarea>
    </div>

    <!-- ===== INPUT (UI component — shows placeholder, editable on dblclick) ===== -->
    <div v-else-if="element.type === 'input'" class="el-input-comp" :style="inputStyle">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" style="flex-shrink:0"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <span v-if="!editing" class="el-input-placeholder">{{ element.placeholder || '请输入内容...' }}</span>
      <input
        v-if="editing"
        ref="textareaRef"
        class="el-input-edit"
        :style="inputEditStyle"
        v-model="localText"
        :placeholder="element.placeholder || '请输入内容...'"
        @blur="commitText"
        @keydown.stop
        @mousedown.stop
        @click.stop
      />
    </div>

    <!-- ===== NAVBAR ===== -->
    <div v-else-if="element.type === 'navbar'" class="el-navbar" :style="navbarStyle">
      <div class="navbar-menu-icon">
        <span></span><span></span><span></span>
      </div>
      <span v-if="!editing" class="el-navbar-title">{{ element.text || 'Navigation' }}</span>
      <textarea
        v-if="editing"
        ref="textareaRef"
        class="el-textarea-inline"
        :style="textareaInlineStyle"
        v-model="localText"
        @blur="commitText"
        @keydown.stop
        @mousedown.stop
        @click.stop
      ></textarea>
      <div class="navbar-actions">
        <span class="navbar-dot"></span>
        <span class="navbar-dot"></span>
        <span class="navbar-dot"></span>
      </div>
    </div>

    <!-- ===== RECTANGLE ===== -->
    <div v-else-if="element.type === 'rectangle'" class="el-rect" :style="rectStyle"></div>

    <!-- ===== CARD ===== -->
    <div v-else-if="element.type === 'card'" class="el-card" :style="cardStyle">
      <div class="card-img" :style="{ background: element.fill || '#4F8EF7' }"></div>
      <div class="card-body">
        <div class="card-line long"></div>
        <div class="card-line short"></div>
        <div class="card-line medium"></div>
      </div>
    </div>

    <!-- ===== CIRCLE ===== -->
    <svg v-else-if="element.type === 'circle'" :width="element.width" :height="element.height" style="display:block;overflow:visible">
      <ellipse
        :cx="element.width/2"
        :cy="element.height/2"
        :rx="Math.max(1, element.width/2 - (element.strokeWidth||0)/2)"
        :ry="Math.max(1, element.height/2 - (element.strokeWidth||0)/2)"
        :fill="element.fill || '#F7874F'"
        :stroke="element.stroke && element.stroke !== 'transparent' ? element.stroke : 'none'"
        :stroke-width="element.strokeWidth || 0"
      />
    </svg>

    <!-- ===== TRIANGLE ===== -->
    <svg v-else-if="element.type === 'triangle'" :width="element.width" :height="element.height" style="display:block">
      <polygon
        :points="`${element.width/2},2 ${element.width-2},${element.height-2} 2,${element.height-2}`"
        :fill="element.fill || '#10b981'"
        :stroke="element.stroke && element.stroke !== 'transparent' ? element.stroke : 'none'"
        :stroke-width="element.strokeWidth || 0"
      />
    </svg>

    <!-- ===== DIVIDER ===== -->
    <div v-else-if="element.type === 'divider'" :style="dividerStyle"></div>

    <!-- ===== ICON ===== -->
    <div v-else-if="element.type === 'icon'" class="el-icon-wrap">
      <svg :width="element.width * 0.65" :height="element.height * 0.65" viewBox="0 0 24 24" :fill="element.fill || '#4F8EF7'">
        <path v-if="element.iconType === 'star' || !element.iconType" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        <path v-else-if="element.iconType === 'heart'" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        <circle v-else cx="12" cy="12" r="10"/>
      </svg>
    </div>

    <!-- ===== IMAGE ===== -->
    <div v-else-if="element.type === 'image'" class="el-image" :style="imageWrapStyle">
      <img v-if="element.src" :src="element.src" class="el-image-img" :style="{ borderRadius: (element.borderRadius||0)+'px' }" />
      <div v-else class="el-image-placeholder">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="#c0c0cc">
          <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
        </svg>
        <span>图片</span>
      </div>
    </div>

    <!-- ===== FALLBACK ===== -->
    <div v-else :style="rectStyle"></div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'

const props = defineProps({
  element: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  editing: { type: Boolean, default: false },
  zoom: { type: Number, default: 1 },
})
const emit = defineEmits(['mousedown', 'dblclick', 'update', 'endEdit'])

const textareaRef = ref(null)
const localText = ref('')

// Sync localText whenever we enter editing mode
watch(() => props.editing, (val) => {
  if (val) {
    // For input type, edit the placeholder; for others edit the text
    if (props.element.type === 'input') {
      localText.value = props.element.placeholder || ''
    } else {
      localText.value = props.element.text || ''
    }
    nextTick(() => {
      if (textareaRef.value) {
        textareaRef.value.focus()
        if (typeof textareaRef.value.select === 'function') {
          textareaRef.value.select()
        }
      }
    })
  }
})

// Also watch element.text to keep localText in sync when panel updates text while editing
watch(() => props.element.text, (val) => {
  if (!props.editing) return  // only update localText if NOT in edit mode (panel-driven updates)
  // Don't override while user is typing in textarea
})

// Watch element.placeholder for input type
watch(() => props.element.placeholder, (val) => {
  if (!props.editing) return
})

function commitText() {
  if (props.editing) {
    if (props.element.type === 'input') {
      emit('update', { placeholder: localText.value })
    } else {
      emit('update', { text: localText.value })
    }
    emit('endEdit')
  }
}

function onWrapperMousedown(e) {
  if (!props.editing) emit('mousedown', e)
}

function onWrapperDblClick(e) {
  emit('dblclick', e)
}

// ─── Styles ────────────────────────────────────────────────────────────────

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
  pointerEvents: props.element.locked ? 'none' : undefined,
  boxSizing: 'border-box',
}))

const textStyle = computed(() => ({
  position: 'relative',
  width: '100%',
  height: '100%',
  color: props.element.color || '#1a1a2e',
  fontSize: (props.element.fontSize || 16) + 'px',
  fontFamily: props.element.fontFamily || 'inherit',
  fontWeight: props.element.fontWeight || 'normal',
  fontStyle: props.element.fontStyle || 'normal',
  textDecoration: props.element.textDecoration || 'none',
  textAlign: props.element.textAlign || 'left',
  lineHeight: props.element.lineHeight || 1.5,
  padding: '4px 6px',
  boxSizing: 'border-box',
  overflow: 'hidden',
  background: 'transparent',
}))

// Textarea overlaid on the text element, matching its exact style
const textareaStyle = computed(() => ({
  position: 'absolute',
  inset: 0,
  width: '100%',
  height: '100%',
  color: props.element.color || '#1a1a2e',
  fontSize: (props.element.fontSize || 16) + 'px',
  fontFamily: props.element.fontFamily || 'inherit',
  fontWeight: props.element.fontWeight || 'normal',
  fontStyle: props.element.fontStyle || 'normal',
  textAlign: props.element.textAlign || 'left',
  lineHeight: props.element.lineHeight || 1.5,
  background: 'rgba(255,255,255,0.05)',
  border: '2px solid #4F8EF7',
  borderRadius: '2px',
  outline: 'none',
  resize: 'none',
  padding: '4px 6px',
  boxSizing: 'border-box',
  overflow: 'auto',
  caretColor: '#4F8EF7',
  zIndex: 10,
}))

const textareaInlineStyle = computed(() => ({
  position: 'absolute',
  inset: 0,
  width: '100%',
  height: '100%',
  color: props.element.color || '#ffffff',
  fontSize: (props.element.fontSize || 14) + 'px',
  textAlign: 'center',
  background: 'transparent',
  border: '2px solid rgba(255,255,255,0.8)',
  outline: 'none',
  resize: 'none',
  padding: '0 8px',
  boxSizing: 'border-box',
  caretColor: '#fff',
  zIndex: 10,
  fontFamily: props.element.fontFamily || 'inherit',
  fontWeight: props.element.fontWeight || '600',
}))

const inputEditStyle = computed(() => ({
  flex: 1,
  background: 'transparent',
  border: 'none',
  outline: 'none',
  color: props.element.color || '#6b7280',
  fontSize: (props.element.fontSize || 14) + 'px',
  fontFamily: props.element.fontFamily || 'inherit',
  width: '100%',
  caretColor: '#4F8EF7',
}))

const rectStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || 'transparent',
  border: (props.element.strokeWidth > 0)
    ? `${props.element.strokeWidth}px solid ${props.element.stroke || 'transparent'}`
    : 'none',
  borderRadius: (props.element.borderRadius || 0) + 'px',
  boxSizing: 'border-box',
  boxShadow: props.element.shadow ? '0 4px 24px rgba(0,0,0,0.12)' : 'none',
}))

const buttonStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#4F8EF7',
  border: (props.element.strokeWidth > 0)
    ? `${props.element.strokeWidth}px solid ${props.element.stroke}`
    : 'none',
  borderRadius: (props.element.borderRadius ?? 8) + 'px',
  color: props.element.color || '#ffffff',
  fontSize: (props.element.fontSize || 14) + 'px',
  fontFamily: props.element.fontFamily || 'inherit',
  fontWeight: props.element.fontWeight || '600',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  boxSizing: 'border-box',
  position: 'relative',
  userSelect: 'none',
  letterSpacing: '0.02em',
  boxShadow: props.element.shadow ? '0 2px 12px rgba(0,0,0,0.18)' : 'none',
}))

const inputStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#ffffff',
  border: `${props.element.strokeWidth ?? 1.5}px solid ${props.element.stroke || '#d1d5db'}`,
  borderRadius: (props.element.borderRadius ?? 8) + 'px',
  display: 'flex',
  alignItems: 'center',
  padding: '0 12px',
  gap: '8px',
  boxSizing: 'border-box',
  position: 'relative',
}))

const navbarStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#ffffff',
  borderBottom: `${props.element.strokeWidth ?? 1}px solid ${props.element.stroke || '#e5e7eb'}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '0 16px',
  boxSizing: 'border-box',
  color: props.element.color || '#1a1a2e',
  fontSize: (props.element.fontSize || 16) + 'px',
  fontFamily: props.element.fontFamily || 'inherit',
  fontWeight: props.element.fontWeight || '600',
  gap: '12px',
  position: 'relative',
}))

const cardStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: '#ffffff',
  border: `${props.element.strokeWidth ?? 1}px solid ${props.element.stroke || '#e5e7eb'}`,
  borderRadius: (props.element.borderRadius ?? 12) + 'px',
  overflow: 'hidden',
  boxSizing: 'border-box',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: props.element.shadow ? '0 4px 24px rgba(0,0,0,0.12)' : 'none',
}))

const dividerStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#e5e7eb',
  borderRadius: (props.element.borderRadius || 0) + 'px',
}))

const imageWrapStyle = computed(() => ({
  width: '100%',
  height: '100%',
  background: props.element.fill || '#f3f4f6',
  border: `${props.element.strokeWidth ?? 1}px solid ${props.element.stroke || '#e5e7eb'}`,
  borderRadius: (props.element.borderRadius || 4) + 'px',
  overflow: 'hidden',
  boxSizing: 'border-box',
}))

const formattedText = computed(() => {
  const t = props.element.text || '双击编辑文本'
  return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/\n/g, '<br>')
})
</script>

<style scoped>
.el-wrapper {
  user-select: none;
  box-sizing: border-box;
}
.el-wrapper.selected {
  outline: 2px solid #4F8EF7;
  outline-offset: 1px;
}

/* TEXT */
.el-text { position: relative; display: flex; flex-direction: column; justify-content: flex-start; }
.el-text-display { width: 100%; height: 100%; white-space: pre-wrap; word-break: break-word; overflow: hidden; }
.el-textarea { font-family: inherit; }

/* BUTTON */
.el-button { position: relative; transition: filter 0.1s; overflow: hidden; }
.el-button:hover { filter: brightness(0.96); }
.el-button-label { pointer-events: none; }
.el-textarea-inline { font-family: inherit; width: 100%; text-align: center; }

/* INPUT COMPONENT */
.el-input-comp { cursor: text; overflow: hidden; }
.el-input-placeholder { color: #9ca3af; font-size: 14px; pointer-events: none; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; flex: 1; }
.el-input-edit { color: #9ca3af; font-size: 14px; flex: 1; min-width: 0; }

/* NAVBAR */
.el-navbar { overflow: hidden; }
.el-navbar-title { flex: 1; text-align: center; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.navbar-menu-icon { display: flex; flex-direction: column; gap: 4px; cursor: pointer; flex-shrink: 0; }
.navbar-menu-icon span { display: block; width: 18px; height: 2px; background: currentColor; border-radius: 1px; }
.navbar-actions { display: flex; gap: 6px; flex-shrink: 0; }
.navbar-dot { width: 5px; height: 5px; background: currentColor; border-radius: 50%; opacity: 0.6; }

/* CARD */
.el-card { }
.card-img { height: 48%; flex-shrink: 0; }
.card-body { flex: 1; padding: 10px 14px; background: #fff; display: flex; flex-direction: column; gap: 7px; justify-content: center; }
.card-line { height: 9px; background: #e5e7eb; border-radius: 4px; }
.card-line.long { width: 90%; }
.card-line.medium { width: 70%; }
.card-line.short { width: 50%; }

/* ICON */
.el-icon-wrap { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }

/* IMAGE */
.el-image { }
.el-image-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.el-image-placeholder { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; color: #9ca3af; font-size: 12px; }
</style>
