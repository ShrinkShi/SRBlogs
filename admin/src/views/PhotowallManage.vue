<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'url', label: '图片 URL', type: 'upload' as const, required: true },
  { key: 'title', label: '标题' },
  { key: 'description', label: '描述', type: 'textarea' as const },
  { key: 'date', label: '日期', placeholder: '2026-05-02' },
  { key: 'tags', label: '标签', type: 'tags' as const, placeholder: '生活, 截图, 旅行' }
]

const emptyItem = { url: '', title: '', description: '', date: '', tags: [] }
</script>

<template>
  <StructuredJsonManager title="照片墙管理" path="/photos" item-name="图片" :fields="fields" :empty-item="emptyItem" />
</template>
