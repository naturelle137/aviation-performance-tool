<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import AppLayout from '@/components/layout/AppLayout.vue'
</script>

<template>
  <Toast position="top-right" />
  <ConfirmDialog />
  <AppLayout>
    <RouterView />
  </AppLayout>
</template>

<style>
/* Global styles are in assets/styles/main.css */
</style>
