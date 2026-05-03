<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'title', label: '歌曲标题', required: true },
  { key: 'artist', label: '艺术家', required: true },
  { key: 'cover', label: '封面 URL', type: 'upload' as const, accept: 'image/*' },
  { key: 'url', label: '歌曲 URL / 本地上传', type: 'upload' as const, accept: 'audio/*,video/*' },
  { key: 'lyricUrl', label: '歌词文件 URL / 本地上传', type: 'upload' as const, accept: '.lrc,.txt,text/plain' },
  { key: 'lyrics', label: '内嵌歌词', type: 'textarea' as const },
  { key: 'id', label: '云音乐 ID' },
  { key: 'sort', label: '排序', type: 'number' as const }
]

const emptyItem = { title: '', artist: '', cover: '', url: '', lyricUrl: '', lyrics: '', id: '', sort: 0 }
</script>

<template>
  <StructuredJsonManager title="歌单管理" path="/music" item-name="歌曲" :fields="fields" :empty-item="emptyItem" />
</template>
