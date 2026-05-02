<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'name', label: '名称', required: true },
  { key: 'url', label: 'URL', required: true, placeholder: 'https://example.com' },
  { key: 'description', label: '描述', type: 'textarea' as const },
  { key: 'avatar', label: '头像/图标 URL', type: 'upload' as const },
  { key: 'tags', label: '标签', type: 'tags' as const, placeholder: 'Vue, Blog, Friend' }
]

const emptyItem = { name: '', url: '', description: '', avatar: '', tags: [] }
</script>

<template>
  <StructuredJsonManager title="友链管理" path="/friends" item-name="友链" :fields="fields" :empty-item="emptyItem" />
</template>
