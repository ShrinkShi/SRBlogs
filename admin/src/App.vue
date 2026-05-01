<script setup lang="ts">
import AdminLayout from '@/components/AdminLayout.vue'
import Toast from '@/components/Toast.vue'
</script>

<template>
  <AdminLayout v-if="$route.path !== '/login'">
    <RouterView />
  </AdminLayout>
  <RouterView v-else />
  <Toast />
</template>
