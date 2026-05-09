<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'name', label: '项目名称', required: true },
  { key: 'description', label: '项目简介', type: 'textarea' as const, required: true },
  { key: 'tags', label: '技术标签', type: 'tags' as const, placeholder: 'Vue3, FastAPI, Tailwind' },
  { key: 'url', label: '项目链接（前台点击跳转）', placeholder: 'https://example.com', required: true },
  { key: 'repo', label: '代码仓库链接' },
  { key: 'cover', label: '封面 URL（留空使用默认封面）', type: 'upload' as const, accept: 'image/*' },
  { key: 'status', label: '状态', type: 'select' as const, options: ['planning', 'active', 'done', 'archived', 'demo', 'notes'] }
]

const emptyItem = { name: '', description: '', tags: [], url: '', repo: '', cover: '', status: 'active' }
</script>

<template>
  <StructuredJsonManager title="项目管理" path="/projects" item-name="项目" :fields="fields" :empty-item="emptyItem" />
</template>
