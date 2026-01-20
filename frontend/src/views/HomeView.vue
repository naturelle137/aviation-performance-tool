<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAircraftStore } from '@/stores'
import Card from 'primevue/card'
import Button from 'primevue/button'

const router = useRouter()
const aircraftStore = useAircraftStore()

const stats = ref([
  { label: 'Aircraft', value: '0', icon: 'pi-briefcase', color: 'var(--color-accent-primary)' },
  { label: 'Calculations Today', value: '0', icon: 'pi-calculator', color: 'var(--color-accent-success)' },
  { label: 'Last Flight', value: '-', icon: 'pi-clock', color: 'var(--color-accent-warning)' },
])

onMounted(async () => {
  try {
    await aircraftStore.fetchAll()
    stats.value[0].value = String(aircraftStore.aircraftCount)
  } catch {
    // Handle error silently for dashboard
  }
})
</script>

<template>
  <div class="home-view animate-fade-in">
    <header class="page-header">
      <h1 class="page-title">
        <span class="text-gradient">Dashboard</span>
      </h1>
      <p class="page-subtitle">Welcome to Aviation Performance Tool</p>
    </header>

    <!-- Stats Cards -->
    <section class="stats-grid">
      <Card v-for="stat in stats" :key="stat.label" class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color + '20', color: stat.color }">
              <i :class="['pi', stat.icon]"></i>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </template>
      </Card>
    </section>

    <!-- Quick Actions -->
    <section class="quick-actions">
      <h2 class="section-title">Quick Actions</h2>
      <div class="actions-grid">
        <Card class="action-card" @click="router.push('/calculation')">
          <template #content>
            <div class="action-content">
              <i class="pi pi-calculator action-icon"></i>
              <h3>New Calculation</h3>
              <p>Calculate M&amp;B and Performance</p>
            </div>
          </template>
        </Card>

        <Card class="action-card" @click="router.push('/aircraft')">
          <template #content>
            <div class="action-content">
              <i class="pi pi-plus-circle action-icon"></i>
              <h3>Add Aircraft</h3>
              <p>Register a new aircraft</p>
            </div>
          </template>
        </Card>

        <Card class="action-card" @click="router.push('/aircraft')">
          <template #content>
            <div class="action-content">
              <i class="pi pi-list action-icon"></i>
              <h3>View Fleet</h3>
              <p>Manage your aircraft</p>
            </div>
          </template>
        </Card>
      </div>
    </section>

    <!-- Recent Aircraft -->
    <section class="recent-section" v-if="aircraftStore.aircraft.length > 0">
      <div class="section-header">
        <h2 class="section-title">Your Aircraft</h2>
        <Button 
          label="View All" 
          class="p-button-text" 
          @click="router.push('/aircraft')"
        />
      </div>
      <div class="aircraft-grid">
        <Card 
          v-for="ac in aircraftStore.aircraft.slice(0, 4)" 
          :key="ac.id" 
          class="aircraft-card"
          @click="router.push(`/aircraft/${ac.id}`)"
        >
          <template #content>
            <div class="aircraft-content">
              <div class="aircraft-reg">{{ ac.registration }}</div>
              <div class="aircraft-type">{{ ac.manufacturer }} {{ ac.aircraft_type }}</div>
              <div class="aircraft-weight">MTOW: {{ ac.mtow_kg }} kg</div>
            </div>
          </template>
        </Card>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-view {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
}

.stat-card {
  cursor: default;
}

.stat-card :deep(.p-card-content) {
  padding: var(--spacing-md);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Quick Actions */
.section-title {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-lg);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
}

.action-card {
  cursor: pointer;
  transition: all var(--transition-normal);
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
}

.action-card :deep(.p-card-content) {
  padding: var(--spacing-lg);
}

.action-content {
  text-align: center;
}

.action-icon {
  font-size: 2rem;
  color: var(--color-accent-primary);
  margin-bottom: var(--spacing-md);
}

.action-content h3 {
  margin-bottom: var(--spacing-xs);
}

.action-content p {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* Recent Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.aircraft-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
}

.aircraft-card {
  cursor: pointer;
}

.aircraft-card :deep(.p-card-content) {
  padding: var(--spacing-md);
}

.aircraft-reg {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-accent-primary);
  margin-bottom: var(--spacing-xs);
}

.aircraft-type {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.aircraft-weight {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
</style>
