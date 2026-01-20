<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAircraftStore } from '@/stores'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'

const route = useRoute()
const router = useRouter()
const aircraftStore = useAircraftStore()

const aircraftId = ref(Number(route.params.id))

onMounted(async () => {
  await aircraftStore.fetchById(aircraftId.value)
})
</script>

<template>
  <div class="aircraft-detail-view animate-fade-in">
    <div v-if="aircraftStore.loading" class="loading-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
    </div>

    <template v-else-if="aircraftStore.currentAircraft">
      <header class="page-header">
        <div>
          <Button
            icon="pi pi-arrow-left"
            class="p-button-text back-button"
            @click="router.push('/aircraft')"
          />
          <h1 class="page-title">
            <span class="text-gradient">{{ aircraftStore.currentAircraft.registration }}</span>
          </h1>
          <p class="page-subtitle">
            {{ aircraftStore.currentAircraft.manufacturer }} 
            {{ aircraftStore.currentAircraft.aircraft_type }}
          </p>
        </div>
        <div class="header-actions">
          <Button
            icon="pi pi-calculator"
            label="New Calculation"
            class="p-button-primary"
            @click="router.push('/calculation')"
          />
        </div>
      </header>

      <!-- Weight & Balance Section -->
      <section class="detail-section">
        <h2 class="section-title">Weight Data</h2>
        <div class="cards-grid">
          <Card class="info-card">
            <template #content>
              <div class="info-label">Empty Weight</div>
              <div class="info-value">{{ aircraftStore.currentAircraft.empty_weight_kg }} kg</div>
              <div class="info-sub">Arm: {{ aircraftStore.currentAircraft.empty_arm_m }} m</div>
            </template>
          </Card>

          <Card class="info-card">
            <template #content>
              <div class="info-label">MTOW</div>
              <div class="info-value">{{ aircraftStore.currentAircraft.mtow_kg }} kg</div>
            </template>
          </Card>

          <Card class="info-card">
            <template #content>
              <div class="info-label">Max Landing Weight</div>
              <div class="info-value">
                {{ aircraftStore.currentAircraft.max_landing_weight_kg || aircraftStore.currentAircraft.mtow_kg }} kg
              </div>
            </template>
          </Card>

          <Card class="info-card">
            <template #content>
              <div class="info-label">Fuel Capacity</div>
              <div class="info-value">{{ aircraftStore.currentAircraft.fuel_capacity_l }} L</div>
              <div class="info-sub">Arm: {{ aircraftStore.currentAircraft.fuel_arm_m }} m</div>
            </template>
          </Card>
        </div>
      </section>

      <!-- Weight Stations -->
      <section class="detail-section" v-if="aircraftStore.currentAircraft.weight_stations?.length">
        <h2 class="section-title">Weight Stations</h2>
        <div class="stations-list">
          <Card 
            v-for="station in aircraftStore.currentAircraft.weight_stations" 
            :key="station.id" 
            class="station-card"
          >
            <template #content>
              <div class="station-name">{{ station.name }}</div>
              <div class="station-details">
                <Chip :label="`Arm: ${station.arm_m} m`" />
                <Chip v-if="station.max_weight_kg" :label="`Max: ${station.max_weight_kg} kg`" />
              </div>
            </template>
          </Card>
        </div>
      </section>

      <!-- CG Envelopes -->
      <section class="detail-section" v-if="aircraftStore.currentAircraft.cg_envelopes?.length">
        <h2 class="section-title">CG Envelopes</h2>
        <div class="envelopes-list">
          <Card 
            v-for="envelope in aircraftStore.currentAircraft.cg_envelopes" 
            :key="envelope.id" 
            class="envelope-card"
          >
            <template #content>
              <div class="envelope-category">{{ envelope.category }}</div>
              <div class="envelope-points">
                {{ envelope.polygon_points.length }} points defined
              </div>
            </template>
          </Card>
        </div>
      </section>

      <!-- Performance Source -->
      <section class="detail-section">
        <h2 class="section-title">Performance Data</h2>
        <Card class="info-card">
          <template #content>
            <div class="info-label">Source</div>
            <div class="info-value">
              <Chip 
                :label="aircraftStore.currentAircraft.performance_source.toUpperCase()" 
                :class="`source-${aircraftStore.currentAircraft.performance_source}`"
              />
            </div>
          </template>
        </Card>
      </section>
    </template>
  </div>
</template>

<style scoped>
.aircraft-detail-view {
  padding-bottom: var(--spacing-2xl);
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  color: var(--color-accent-primary);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xl);
}

.back-button {
  margin-bottom: var(--spacing-sm);
}

.page-title {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-xs);
}

.page-subtitle {
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}

.detail-section {
  margin-bottom: var(--spacing-2xl);
}

.section-title {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-lg);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.info-card :deep(.p-card-content) {
  padding: var(--spacing-md);
}

.info-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.info-value {
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.info-sub {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-top: var(--spacing-xs);
}

.stations-list,
.envelopes-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.station-card,
.envelope-card {
  min-width: 200px;
}

.station-card :deep(.p-card-content),
.envelope-card :deep(.p-card-content) {
  padding: var(--spacing-md);
}

.station-name,
.envelope-category {
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  text-transform: capitalize;
}

.station-details {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

.envelope-points {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.source-fsm375 {
  background: var(--color-accent-success) !important;
}

.source-manufacturer {
  background: var(--color-accent-primary) !important;
}

.source-custom {
  background: var(--color-accent-secondary) !important;
}
</style>
