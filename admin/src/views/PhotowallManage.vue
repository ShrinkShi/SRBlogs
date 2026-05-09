<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'title', label: '相册标题', required: true },
  { key: 'description', label: '相册描述', type: 'textarea' as const },
  { key: 'cover', label: '封面 URL（留空默认第一张）', type: 'upload' as const, accept: 'image/*' },
  { key: 'date', label: '日期', placeholder: '2026-05-02' },
  { key: 'tags', label: '标签', type: 'tags' as const, placeholder: '生活, 截图, 旅行' },
  { key: 'photos', label: '相册照片（最多 50 张）', type: 'gallery' as const, required: true }
]

const emptyItem = { title: '', description: '', cover: '', date: '', tags: [], photos: [] }
</script>

<template>
  <StructuredJsonManager title="图片管理" path="/photos" item-name="相册" :fields="fields" :empty-item="emptyItem" />
</template>
