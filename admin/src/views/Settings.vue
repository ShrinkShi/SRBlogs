<script setup lang="ts">
import GlassCard from '@/components/GlassCard.vue'
import SettingsPanels from '@/components/SettingsPanels.vue'
</script>
<template>
  <section class="grid gap-5">
    <GlassCard><h1 class="text-4xl font-black text-white">设置</h1><p class="mt-2 text-white/50">图床、AI、部署等配置。敏感密钥应写入后端 .env，不应存前端。</p></GlassCard>
    <SettingsPanels />
  </section>
</template>
