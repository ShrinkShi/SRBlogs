<script setup lang="ts">
import StructuredJsonManager from '@/components/StructuredJsonManager.vue'

const fields = [
  { key: 'title', label: '歌曲标题', required: true },
  { key: 'artist', label: '歌手', required: true },
  { key: 'cover', label: '封面 URL', type: 'upload' as const, accept: 'image/*' },
  { key: 'url', label: '音频文件 / URL', type: 'upload' as const, accept: 'audio/*,video/*' },
  { key: 'lyricUrl', label: '歌词文件 / URL', type: 'upload' as const, accept: '.lrc,.txt,text/plain' },
  { key: 'lyrics', label: '内嵌歌词', type: 'textarea' as const },
  { key: 'id', label: '歌曲 ID' },
  { key: 'sort', label: '排序', type: 'number' as const },
  { key: 'likes', label: '喜欢数', type: 'number' as const }
]

const emptyItem = { title: '', artist: '', cover: '', url: '', lyricUrl: '', lyrics: '', id: '', sort: 0, likes: 0 }
</script>

<template>
  <StructuredJsonManager
    title="音乐管理"
    path="/music"
    item-name="歌曲"
    :fields="fields"
    :empty-item="emptyItem"
    comment-resource="music"
    comment-type-label="音乐"
  />
</template>
