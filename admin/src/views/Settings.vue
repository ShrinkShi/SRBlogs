<script setup lang="ts">
import GlassCard from '@/components/GlassCard.vue'
import SettingsPanels from '@/components/SettingsPanels.vue'
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="relative z-[1]">
        <h1 class="text-4xl font-black text-white">后台设置</h1>
        <p class="mt-2 text-white/50">站点公开信息、主题背景、留言、图床、AI、部署安全和交互开关集中配置。敏感密钥只保存在后端，不回显明文。</p>
      </div>
    </GlassCard>
    <SettingsPanels />
  </section>
</template>
