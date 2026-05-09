<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'name', label: '站点名称', required: true },
  { key: 'url', label: '站点链接（前台点击跳转）', required: true, placeholder: 'https://example.com' },
  { key: 'description', label: '站点简介', type: 'textarea' as const },
  { key: 'avatar', label: '封面 / 图标 URL（留空使用默认封面）', type: 'upload' as const, accept: 'image/*' },
  { key: 'tags', label: '标签', type: 'tags' as const, placeholder: 'Vue, Blog, Friend' }
]

const emptyItem = { name: '', url: '', description: '', avatar: '', tags: [] }
</script>

<template>
  <StructuredJsonManager title="友链管理" path="/friends" item-name="友链" :fields="fields" :empty-item="emptyItem" />
</template>
