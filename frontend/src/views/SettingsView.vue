<script setup lang="ts">
import Card from 'primevue/card'
</script>

<template>
  <div class="settings-view animate-fade-in">
    <header class="page-header">
      <h1 class="page-title">
        <span class="text-gradient">Settings</span>
      </h1>
      <p class="page-subtitle">Configure your application preferences</p>
    </header>

    <Card class="settings-card">
      <template #title>Application Settings</template>
      <template #content>
        <p class="placeholder-text">
          Settings will be available in a future update.
        </p>
        <ul class="future-features">
          <li>OAuth authentication (Google/Apple)</li>
          <li>Default units (metric/imperial)</li>
          <li>Weather API key configuration</li>
          <li>PDF export templates</li>
          <li>Data backup/restore</li>
        </ul>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.settings-view {
  padding-bottom: var(--spacing-2xl);
}

.page-header {
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-xs);
}

.page-subtitle {
  color: var(--color-text-secondary);
}

.settings-card {
  max-width: 600px;
}

.placeholder-text {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
}

.future-features {
  color: var(--color-text-muted);
  padding-left: var(--spacing-lg);
}

.future-features li {
  margin-bottom: var(--spacing-sm);
}
</style>
