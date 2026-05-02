<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'name', label: '名称', required: true },
  { key: 'description', label: '描述', type: 'textarea' as const, required: true },
  { key: 'tags', label: '技术栈', type: 'tags' as const, placeholder: 'Vue3, FastAPI, Tailwind' },
  { key: 'url', label: '项目链接', placeholder: 'https://example.com' },
  { key: 'repo', label: 'GitHub/Gitee 链接' },
  { key: 'cover', label: '封面 URL', type: 'upload' as const },
  { key: 'status', label: '状态', type: 'select' as const, options: ['planning', 'active', 'done', 'archived', 'demo', 'notes'] }
]

const emptyItem = { name: '', description: '', tags: [], url: '', repo: '', cover: '', status: 'active' }
</script>

<template>
  <StructuredJsonManager title="项目管理" path="/projects" item-name="项目" :fields="fields" :empty-item="emptyItem" />
</template>
