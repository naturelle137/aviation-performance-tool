<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Menubar from 'primevue/menubar'
import Button from 'primevue/button'

const router = useRouter()

const menuItems = ref([
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    command: () => router.push('/')
  },
  {
    label: 'Aircraft',
    icon: 'pi pi-briefcase',
    command: () => router.push('/aircraft')
  },
  {
    label: 'Calculation',
    icon: 'pi pi-calculator',
    command: () => router.push('/calculation')
  },
  {
    label: 'Settings',
    icon: 'pi pi-cog',
    command: () => router.push('/settings')
  }
])
</script>

<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="app-header glass">
      <div class="header-content">
        <div class="logo" @click="router.push('/')">
          <i class="pi pi-send logo-icon"></i>
          <span class="logo-text text-gradient">Aviation Performance</span>
        </div>
        
        <Menubar :model="menuItems" class="main-menu" />
        
        <div class="header-actions">
          <Button
            icon="pi pi-plus"
            label="New Calculation"
            class="p-button-primary"
            @click="router.push('/calculation')"
          />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <div class="container">
        <slot />
      </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="container">
        <p class="footer-text">
          Aviation Performance Tool v0.1.0 | 
          <span class="status-success">● API Connected</span>
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  gap: var(--spacing-lg);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.logo:hover {
  opacity: 0.8;
}

.logo-icon {
  font-size: 1.5rem;
  color: var(--color-accent-primary);
  transform: rotate(-45deg);
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: 700;
}

.main-menu {
  background: transparent !important;
  border: none !important;
}

.main-menu :deep(.p-menuitem-link) {
  border-radius: var(--radius-md) !important;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.app-main {
  flex: 1;
  padding: var(--spacing-xl) 0;
}

.app-footer {
  padding: var(--spacing-md) 0;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  background: var(--color-bg-secondary);
}

.footer-text {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
  }

  .main-menu {
    order: 3;
    width: 100%;
  }

  .header-actions {
    display: none;
  }
}
</style>
