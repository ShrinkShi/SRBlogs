<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
const ui = useUiStore(); const content = ref('')
const editorOpen = ref(false)
onMounted(async()=>{ content.value = (await adminApi.json<{content:string}>('/about')).content })
async function save(){ await adminApi.putJson('/about', { content: content.value }); ui.show('关于页已保存') }
function closeEditor(){ if (confirm('确认关闭关于页 Markdown 编辑器？未保存内容请先保存。')) editorOpen.value = false }
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-4xl font-black">关于页面</h1>
          <p class="mt-2 text-sm text-white/55">使用近全屏 Markdown 编辑器维护关于页正文。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button class="rounded-2xl border border-white/10 px-5 py-3 text-white/72" @click="editorOpen = true">打开 Markdown 编辑器</button>
          <button class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950" @click="save">保存</button>
        </div>
      </div>
    </GlassCard>
    <Teleport to="body">
      <div v-if="editorOpen" class="fixed inset-0 z-[9990] bg-slate-950/82 p-3 backdrop-blur-xl md:p-6">
        <div class="mx-auto grid h-full max-w-[1500px] grid-rows-[auto_minmax(0,1fr)] gap-4 rounded-[32px] border border-white/12 bg-slate-950/88 p-4 shadow-2xl">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <h2 class="text-2xl font-black text-white">关于页 Markdown</h2>
            <div class="flex gap-2">
              <button class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950" @click="save">保存</button>
              <button class="rounded-2xl border border-white/10 px-5 py-3 text-white/72" @click="closeEditor">关闭</button>
            </div>
          </div>
          <div class="min-h-0 overflow-auto"><MarkdownEditor v-model="content" /></div>
        </div>
      </div>
    </Teleport>
  </section>
</template>
