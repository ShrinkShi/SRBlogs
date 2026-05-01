<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'
const props = defineProps<{ section: 'posts' | 'moments' | 'chatters'; title: string }>()
const ui = useUiStore()
const items = ref<ContentItem[]>([])
async function load(){ items.value = await adminApi.list(props.section) }
async function remove(slug: string){ if(confirm(`确认删除 ${slug}?`)){ await adminApi.remove(props.section, slug); ui.show('已删除'); await load() } }
onMounted(load)
</script>
<template>
  <section class="grid gap-5">
    <GlassCard><div class="flex items-center justify-between gap-4"><h1 class="text-4xl font-black text-white">{{ title }}</h1><RouterLink :to="`/editor/${section}`" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950">新建</RouterLink></div></GlassCard>
    <GlassCard>
      <div class="grid gap-3">
        <div v-for="item in items" :key="item.slug" class="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 md:flex-row md:items-center md:justify-between">
          <div><h2 class="font-bold text-white">{{ item.meta.title }} <span v-if="item.meta.draft" class="ml-2 rounded-full bg-amber-300/20 px-2 py-1 text-xs text-amber-100">草稿</span></h2><p class="text-sm text-white/45">{{ item.slug }} · {{ item.meta.date }}</p></div>
          <div class="flex gap-2"><RouterLink :to="`/editor/${section}/${item.slug}`" class="rounded-xl bg-white/10 px-3 py-2 text-sm">编辑</RouterLink><button class="rounded-xl bg-red-500/20 px-3 py-2 text-sm text-red-100" @click="remove(item.slug)">删除</button></div>
        </div>
      </div>
    </GlassCard>
  </section>
</template>
