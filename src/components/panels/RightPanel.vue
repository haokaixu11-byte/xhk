<template>
  <aside class="right-panel" @keydown.stop @keyup.stop>
    <div v-if="!sel" class="no-selection">
      <div class="no-sel-icon">☰</div>
      <div>选择元素以编辑属性</div>
      <div class="page-props-section">
        <div class="section-title">页面设置</div>
        <div class="prop-row">
          <label>背景色</label>
          <input type="color" :value="currentPage.background || '#f8f9fa'" @input="updatePageBg($event.target.value)" class="color-input" />
        </div>
        <div class="prop-row">
          <label>宽度</label>
          <input type="number" :value="currentPage.width || 1440" @change="updatePageSize('width', $event.target.value)" class="num-input" />
        </div>
        <div class="prop-row">
          <label>高度</label>
          <input type="number" :value="currentPage.height || 900" @change="updatePageSize('height', $event.target.value)" class="num-input" />
        </div>
      </div>
    </div>

    <div v-else class="props-content">
      <!-- Element Name & Type -->
      <div class="el-header">
        <span class="el-type-badge">{{ typeLabel }}</span>
        <input
          class="el-name-input"
          v-model="elementName"
          @blur="commitElementName"
          placeholder="元素名称"
        />
      </div>

      <!-- Position & Size -->
      <div class="section">
        <div class="section-title">位置与尺寸</div>
        <div class="prop-grid-4">
          <div class="prop-cell">
            <label>X</label>
            <input type="number" :value="Math.round(sel.x)" @change="commitProp('x', +$event.target.value)" class="num-input" />
          </div>
          <div class="prop-cell">
            <label>Y</label>
            <input type="number" :value="Math.round(sel.y)" @change="commitProp('y', +$event.target.value)" class="num-input" />
          </div>
          <div class="prop-cell">
            <label>W</label>
            <input type="number" :value="Math.round(sel.width)" @change="commitProp('width', +$event.target.value)" class="num-input" min="1" />
          </div>
          <div class="prop-cell">
            <label>H</label>
            <input type="number" :value="Math.round(sel.height)" @change="commitProp('height', +$event.target.value)" class="num-input" min="1" />
          </div>
        </div>
        <div class="prop-grid-2">
          <div class="prop-cell">
            <label>旋转</label>
            <div class="input-suffix"><input type="number" :value="sel.rotation || 0" @change="commitProp('rotation', +$event.target.value)" class="num-input" /><span>°</span></div>
          </div>
          <div class="prop-cell">
            <label>圆角</label>
            <input type="number" :value="sel.borderRadius || 0" @change="commitProp('borderRadius', +$event.target.value)" class="num-input" min="0" />
          </div>
        </div>
      </div>

      <!-- Opacity -->
      <div class="section">
        <div class="section-title">透明度</div>
        <div class="opacity-row">
          <input type="range" min="0" max="100" :value="sel.opacity ?? 100" @input="updateProp('opacity', +$event.target.value)" class="range-input" />
          <input type="number" :value="sel.opacity ?? 100" @change="commitProp('opacity', Math.min(100, Math.max(0, +$event.target.value)))" class="num-input small" min="0" max="100" />
        </div>
      </div>

      <!-- Fill & Stroke -->
      <div class="section" v-if="!['text','divider','circle','triangle'].includes(sel.type)">
        <div class="section-title">填充与描边</div>
        <div class="prop-row">
          <label>填充</label>
          <div class="color-row">
            <input type="color" :value="sel.fill || '#ffffff'" @input="updateProp('fill', $event.target.value)" class="color-input" />
            <input class="text-input" :value="sel.fill || '#ffffff'" @change="commitProp('fill', $event.target.value)" />
          </div>
        </div>
        <div class="prop-row">
          <label>描边</label>
          <div class="color-row">
            <input type="color" :value="sel.stroke || '#000000'" @input="updateProp('stroke', $event.target.value)" class="color-input" />
            <input class="text-input" :value="sel.stroke || 'transparent'" @change="commitProp('stroke', $event.target.value)" />
          </div>
        </div>
        <div class="prop-row">
          <label>描边宽</label>
          <input type="number" :value="sel.strokeWidth || 0" @change="commitProp('strokeWidth', +$event.target.value)" class="num-input" min="0" />
        </div>
        <div class="prop-row" v-if="sel.type === 'card'">
          <label>阴影</label>
          <label class="toggle"><input type="checkbox" :checked="sel.shadow" @change="commitProp('shadow', $event.target.checked)" /><span></span></label>
        </div>
      </div>

      <!-- Shape color (circle/triangle) -->
      <div class="section" v-if="['circle','triangle'].includes(sel.type)">
        <div class="section-title">填充与描边</div>
        <div class="prop-row">
          <label>填充</label>
          <div class="color-row">
            <input type="color" :value="sel.fill || '#4F8EF7'" @input="updateProp('fill', $event.target.value)" class="color-input" />
            <input class="text-input" :value="sel.fill || '#4F8EF7'" @change="commitProp('fill', $event.target.value)" />
          </div>
        </div>
        <div class="prop-row">
          <label>描边</label>
          <div class="color-row">
            <input type="color" :value="sel.stroke || '#000000'" @input="updateProp('stroke', $event.target.value)" class="color-input" />
            <input type="number" :value="sel.strokeWidth || 0" @change="commitProp('strokeWidth', +$event.target.value)" class="num-input" min="0" style="width:52px" />
          </div>
        </div>
      </div>

      <!-- Text Properties -->
      <div class="section" v-if="hasText">
        <div class="section-title">文字</div>
        <div class="prop-row" v-if="sel.type === 'text'">
          <label>内容</label>
          <textarea class="text-area" v-model="selText" @blur="commitProp('text', sel.text)" rows="3"></textarea>
        </div>
        <div v-else-if="sel.type === 'input'" class="prop-row">
          <label>占位符</label>
          <input class="text-input" v-model="selPlaceholder" @blur="commitProp('placeholder', sel.placeholder)" placeholder="请输入内容..." />
        </div>
        <div v-else class="prop-row">
          <label>内容</label>
          <input class="text-input" v-model="selText" @blur="commitProp('text', sel.text)" />
        </div>
        <div class="prop-row">
          <label>颜色</label>
          <div class="color-row">
            <input type="color" :value="sel.color || '#1a1a2e'" @input="updateProp('color', $event.target.value)" class="color-input" />
            <input class="text-input" :value="sel.color || '#1a1a2e'" @change="commitProp('color', $event.target.value)" />
          </div>
        </div>
        <div class="prop-grid-2">
          <div class="prop-cell">
            <label>字号</label>
            <input type="number" :value="sel.fontSize || 16" @change="commitProp('fontSize', +$event.target.value)" class="num-input" min="6" />
          </div>
          <div class="prop-cell">
            <label>行高</label>
            <input type="number" :value="sel.lineHeight || 1.5" @change="commitProp('lineHeight', +$event.target.value)" class="num-input" min="0.5" step="0.1" />
          </div>
        </div>
        <div class="prop-row">
          <label>字体</label>
          <select class="select-input" :value="sel.fontFamily || 'Inter, sans-serif'" @change="commitProp('fontFamily', $event.target.value)">
            <option value="Inter, sans-serif">Inter</option>
            <option value="'PingFang SC', sans-serif">PingFang SC</option>
            <option value="Georgia, serif">Georgia</option>
            <option value="'Courier New', monospace">Courier New</option>
            <option value="Arial, sans-serif">Arial</option>
          </select>
        </div>
        <div class="prop-row">
          <label>粗细</label>
          <select class="select-input" :value="sel.fontWeight || 'normal'" @change="commitProp('fontWeight', $event.target.value)">
            <option value="normal">Regular</option>
            <option value="500">Medium</option>
            <option value="600">SemiBold</option>
            <option value="bold">Bold</option>
          </select>
        </div>
        <div class="prop-row">
          <label>对齐</label>
          <div class="btn-group">
            <button :class="{ active: (sel.textAlign || 'left') === 'left' }" @click="updateProp('textAlign', 'left')">⬜L</button>
            <button :class="{ active: sel.textAlign === 'center' }" @click="updateProp('textAlign', 'center')">⊕C</button>
            <button :class="{ active: sel.textAlign === 'right' }" @click="updateProp('textAlign', 'right')">⬜R</button>
          </div>
        </div>
        <div class="prop-row">
          <label>样式</label>
          <div class="btn-group">
            <button :class="{ active: sel.fontStyle === 'italic' }" @click="toggleStyle('fontStyle', 'italic', 'normal')"><i>I</i></button>
            <button :class="{ active: sel.textDecoration === 'underline' }" @click="toggleStyle('textDecoration', 'underline', 'none')"><u>U</u></button>
            <button :class="{ active: sel.textDecoration === 'line-through' }" @click="toggleStyle('textDecoration', 'line-through', 'none')"><s>S</s></button>
          </div>
        </div>
      </div>

      <!-- Image -->
      <div class="section" v-if="sel.type === 'image'">
        <div class="section-title">图片</div>
        <div class="prop-row">
          <label>链接</label>
          <input class="text-input" :value="sel.src || ''" @change="commitProp('src', $event.target.value)" placeholder="输入图片URL..." />
        </div>
      </div>

      <!-- Icon type -->
      <div class="section" v-if="sel.type === 'icon'">
        <div class="section-title">图标</div>
        <div class="prop-row">
          <label>类型</label>
          <select class="select-input" :value="sel.iconType || 'star'" @change="commitProp('iconType', $event.target.value)">
            <option value="star">星星</option>
            <option value="heart">心形</option>
            <option value="circle">圆形</option>
          </select>
        </div>
        <div class="prop-row">
          <label>颜色</label>
          <input type="color" :value="sel.fill || '#4F8EF7'" @input="updateProp('fill', $event.target.value)" class="color-input" />
        </div>
      </div>

      <!-- Visibility & Lock -->
      <div class="section">
        <div class="section-title">状态</div>
        <div class="prop-row">
          <label>可见</label>
          <label class="toggle"><input type="checkbox" :checked="sel.visible !== false" @change="commitProp('visible', $event.target.checked)" /><span></span></label>
        </div>
        <div class="prop-row">
          <label>锁定</label>
          <label class="toggle"><input type="checkbox" :checked="sel.locked" @change="commitProp('locked', $event.target.checked)" /><span></span></label>
        </div>
        <div class="prop-row">
          <label>层级</label>
          <input type="number" :value="sel.zIndex || 0" @change="commitProp('zIndex', +$event.target.value)" class="num-input" min="0" />
        </div>
      </div>

      <!-- Delete -->
      <div class="section">
        <button class="delete-btn" @click="removeSelected">🗑 删除元素</button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { store, currentPage, selectedElements, updateElement, removeSelected, saveHistory } from '../../store/editorStore.js'

const sel = computed(() => selectedElements.value.length === 1 ? selectedElements.value[0] : null)
const typeLabels = { rectangle: '矩形', circle: '圆形', triangle: '三角形', text: '文本', button: '按钮', input: '输入框', card: '卡片', navbar: '导航栏', image: '图片', icon: '图标', divider: '分割线' }
const typeLabel = computed(() => typeLabels[sel.value?.type] || sel.value?.type || '')
const hasText = computed(() => ['text', 'button', 'navbar', 'input'].includes(sel.value?.type))

// ─── 元素名称 与 text/placeholder 保持完全双向同步 ───────────────────────────
// "元素名称"框始终显示并编辑当前组件的主文字内容（text 或 placeholder），
// 画布里修改文字时它也跟着变；在名称框输入时同步写回 text/placeholder。

// 判断当前选中元素使用哪个字段作为"主文字"
const textField = computed(() => {
  if (!sel.value) return null
  if (sel.value.type === 'input') return 'placeholder'
  if (['text', 'button', 'navbar'].includes(sel.value.type)) return 'text'
  return null  // 非文字类组件（矩形、圆形等）不做联动
})

// elementName：双向绑定到 element[textField]
// get → 永远从 store 读最新值，保证画布改完后名称框立即刷新
// set → 写回 store（实时，不保存历史；blur 时 commitProp 存历史）
const elementName = computed({
  get: () => {
    const f = textField.value
    if (f && sel.value) return sel.value[f] ?? ''
    // 非文字类：显示 element.name
    return sel.value?.name ?? ''
  },
  set: (v) => {
    const f = textField.value
    if (f && sel.value) {
      updateProp(f, v)      // 同步到 text/placeholder
    } else if (sel.value) {
      updateProp('name', v) // 非文字类：只改 name
    }
  },
})

// v-model helpers for the dedicated text-content section (同样双向)
const selText = computed({
  get: () => sel.value?.text ?? '',
  set: (v) => updateProp('text', v),
})
const selPlaceholder = computed({
  get: () => sel.value?.placeholder ?? '',
  set: (v) => updateProp('placeholder', v),
})

function updateProp(key, value) {
  if (sel.value) {
    updateElement(sel.value.id, { [key]: value })
  }
}

function commitProp(key, value) {
  if (sel.value) {
    updateElement(sel.value.id, { [key]: value })
    saveHistory()
  }
}

// 元素名称框 blur 时：把最新值同时写回 text/placeholder（视类型）并保存历史
function commitElementName() {
  if (!sel.value) return
  const f = textField.value
  if (f) {
    commitProp(f, sel.value[f] ?? '')  // text 或 placeholder 已通过 v-model set 实时写入，这里只触发 saveHistory
  } else {
    commitProp('name', sel.value.name ?? '')
  }
}

function toggleStyle(prop, activeVal, inactiveVal) {
  if (sel.value) {
    commitProp(prop, sel.value[prop] === activeVal ? inactiveVal : activeVal)
  }
}

function updatePageBg(val) {
  if (currentPage.value) currentPage.value.background = val
}

function updatePageSize(key, val) {
  if (currentPage.value) currentPage.value[key] = Math.max(100, +val)
}
</script>

<style scoped>
.right-panel {
  width: 240px;
  min-width: 240px;
  height: 100%;
  background: #18182a;
  border-left: 1px solid #2a2a3e;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', sans-serif;
}
.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px 16px;
  color: #555;
  font-size: 12px;
  text-align: center;
  gap: 6px;
}
.no-sel-icon { font-size: 28px; margin-bottom: 4px; }
.page-props-section { width: 100%; margin-top: 16px; }
.props-content { padding: 12px 14px; display: flex; flex-direction: column; gap: 0; }
.el-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.el-type-badge { background: #252540; color: #4F8EF7; font-size: 10px; padding: 3px 8px; border-radius: 12px; flex-shrink: 0; font-weight: 600; }
.el-name-input { flex: 1; background: #1e1e30; border: 1px solid #2a2a3e; color: #e0e0f0; border-radius: 6px; padding: 5px 8px; font-size: 12px; outline: none; min-width: 0; }
.el-name-input:focus { border-color: #4F8EF7; }
.section { margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #1e1e30; }
.section-title { font-size: 10px; color: #5a5a7a; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-bottom: 8px; }
.prop-row { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }
.prop-row label { font-size: 11px; color: #7a7a9a; width: 52px; flex-shrink: 0; }
.prop-grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 6px; margin-bottom: 7px; }
.prop-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 7px; }
.prop-cell { display: flex; flex-direction: column; gap: 3px; }
.prop-cell label { font-size: 10px; color: #5a5a7a; }
.num-input { background: #1e1e30; border: 1px solid #2a2a3e; color: #e0e0f0; border-radius: 6px; padding: 5px 7px; font-size: 12px; width: 100%; outline: none; box-sizing: border-box; }
.num-input.small { width: 48px; flex-shrink: 0; }
.num-input:focus { border-color: #4F8EF7; }
.text-input { flex: 1; background: #1e1e30; border: 1px solid #2a2a3e; color: #e0e0f0; border-radius: 6px; padding: 5px 8px; font-size: 12px; outline: none; min-width: 0; box-sizing: border-box; }
.text-input:focus { border-color: #4F8EF7; }
.text-area { flex: 1; background: #1e1e30; border: 1px solid #2a2a3e; color: #e0e0f0; border-radius: 6px; padding: 6px 8px; font-size: 12px; outline: none; resize: vertical; min-width: 0; box-sizing: border-box; font-family: inherit; }
.text-area:focus { border-color: #4F8EF7; }
.color-input { width: 28px; height: 28px; border: 1px solid #2a2a3e; border-radius: 5px; cursor: pointer; padding: 1px; background: none; }
.color-row { display: flex; align-items: center; gap: 6px; flex: 1; }
.opacity-row { display: flex; align-items: center; gap: 8px; }
.range-input { flex: 1; accent-color: #4F8EF7; }
.select-input { flex: 1; background: #1e1e30; border: 1px solid #2a2a3e; color: #e0e0f0; border-radius: 6px; padding: 5px 8px; font-size: 12px; outline: none; }
.select-input:focus { border-color: #4F8EF7; }
.btn-group { display: flex; gap: 4px; }
.btn-group button { background: #1e1e30; border: 1px solid #2a2a3e; color: #9ca3af; border-radius: 5px; padding: 4px 8px; font-size: 12px; cursor: pointer; transition: all 0.1s; }
.btn-group button.active, .btn-group button:hover { background: #252540; border-color: #4F8EF7; color: #4F8EF7; }
.input-suffix { display: flex; align-items: center; gap: 4px; flex: 1; }
.input-suffix span { color: #5a5a7a; font-size: 11px; }
.toggle { display: inline-flex; align-items: center; cursor: pointer; }
.toggle input { display: none; }
.toggle span { width: 34px; height: 18px; background: #2a2a3e; border-radius: 10px; position: relative; transition: background 0.2s; display: block; }
.toggle span::after { content: ''; position: absolute; width: 14px; height: 14px; background: #fff; border-radius: 50%; top: 2px; left: 2px; transition: transform 0.2s; }
.toggle input:checked ~ span { background: #4F8EF7; }
.toggle input:checked ~ span::after { transform: translateX(16px); }
.delete-btn { width: 100%; padding: 9px; background: #2a1515; border: 1px solid #442222; border-radius: 8px; color: #ef4444; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.delete-btn:hover { background: #3a1515; border-color: #ef4444; }
</style>
