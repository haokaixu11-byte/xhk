<template>
  <Teleport to="body">
    <div class="ctx-backdrop" @mousedown.self="$emit('close')"></div>
    <div class="ctx-menu" :style="{ left: x + 'px', top: y + 'px' }">
      <div class="ctx-item" @click="$emit('action', 'copy')"><span>复制</span><span class="ctx-shortcut">⌘C</span></div>
      <div class="ctx-item" @click="$emit('action', 'paste')"><span>粘贴</span><span class="ctx-shortcut">⌘V</span></div>
      <div class="ctx-item" @click="$emit('action', 'duplicate')"><span>重复</span><span class="ctx-shortcut">⌘D</span></div>
      <div class="ctx-divider"></div>
      <div class="ctx-item" :class="{ disabled: !hasSelection }" @click="hasSelection && $emit('action', 'bringToFront')"><span>移到最顶层</span></div>
      <div class="ctx-item" :class="{ disabled: !hasSelection }" @click="hasSelection && $emit('action', 'bringForward')"><span>上移一层</span></div>
      <div class="ctx-item" :class="{ disabled: !hasSelection }" @click="hasSelection && $emit('action', 'sendBackward')"><span>下移一层</span></div>
      <div class="ctx-item" :class="{ disabled: !hasSelection }" @click="hasSelection && $emit('action', 'sendToBack')"><span>移到最底层</span></div>
      <div class="ctx-divider"></div>
      <div class="ctx-item danger" :class="{ disabled: !hasSelection }" @click="hasSelection && $emit('action', 'delete')"><span>删除</span><span class="ctx-shortcut">Del</span></div>
    </div>
  </Teleport>
</template>
<script setup>
defineProps({ x: Number, y: Number, hasSelection: Boolean })
defineEmits(['close', 'action'])
</script>
<style scoped>
.ctx-backdrop { position:fixed; inset:0; z-index:9998; }
.ctx-menu { position:fixed; z-index:9999; background:#fff; border:1px solid #e5e7eb; border-radius:10px; box-shadow:0 8px 32px rgba(0,0,0,0.14); padding:6px 0; min-width:180px; font-size:13px; font-family:'Inter',sans-serif; }
.ctx-item { display:flex; align-items:center; justify-content:space-between; padding:8px 16px; cursor:pointer; color:#1a1a2e; transition:background 0.1s; }
.ctx-item:hover { background:#f3f4ff; }
.ctx-item.danger { color:#ef4444; }
.ctx-item.danger:hover { background:#fef2f2; }
.ctx-item.disabled { opacity:0.4; pointer-events:none; }
.ctx-shortcut { color:#9ca3af; font-size:11px; }
.ctx-divider { height:1px; background:#f0f0f5; margin:4px 0; }
</style>
