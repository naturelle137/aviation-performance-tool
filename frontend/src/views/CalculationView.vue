<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAircraftStore, useCalculationStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import Message from 'primevue/message'
import LoadingStation from '@/components/LoadingStation.vue'
import CGEnvelopeChart from '@/components/charts/CGEnvelopeChart.vue'
import type { WeightInput, RunwayCondition } from '@/types'

const toast = useToast()
const aircraftStore = useAircraftStore()
const calculationStore = useCalculationStore()

const selectedAircraftId = ref<number | null>(null)
const fuelLiters = ref(0)
const tripFuelLiters = ref(0)
const weightInputs = ref<WeightInput[]>([])

// Performance inputs
const pressureAltitude = ref(0)
const temperature = ref(15)
const windComponent = ref(0)
const runwayCondition = ref<RunwayCondition>('dry')
const runwaySlope = ref(0)

const runwayConditions = [
  { label: 'Dry', value: 'dry' },
  { label: 'Wet', value: 'wet' },
  { label: 'Grass', value: 'grass' },
]

onMounted(async () => {
  await aircraftStore.fetchAll()
})

const selectedAircraft = computed(() => {
  if (!selectedAircraftId.value) return null
  return aircraftStore.getAircraftById(selectedAircraftId.value)
})

function onAircraftChange(): void {
  if (selectedAircraftId.value) {
    aircraftStore.fetchById(selectedAircraftId.value).then(() => {
      // Initialize weight inputs from stations
      if (aircraftStore.currentAircraft?.weight_stations) {
        weightInputs.value = aircraftStore.currentAircraft.weight_stations.map((s) => ({
          station_name: s.name,
          weight_kg: s.default_weight_kg || 0,
        }))
      }
    })
  }
}

async function calculateMassBalance(): Promise<void> {
  if (!selectedAircraftId.value) {
    toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: 'Please select an aircraft',
      life: 3000,
    })
    return
  }

  try {
    await calculationStore.calculateMassBalance({
      aircraft_id: selectedAircraftId.value,
      weight_inputs: weightInputs.value,
      fuel_liters: fuelLiters.value,
      trip_fuel_liters: tripFuelLiters.value,
    })

    toast.add({
      severity: 'success',
      summary: 'Calculated',
      detail: 'Mass & Balance calculation complete',
      life: 3000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Calculation failed',
      life: 5000,
    })
  }
}

async function calculatePerformance(): Promise<void> {
  if (!selectedAircraftId.value || !calculationStore.massBalanceResult) {
    toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: 'Please calculate M&B first',
      life: 3000,
    })
    return
  }

  try {
    await calculationStore.calculatePerformance({
      aircraft_id: selectedAircraftId.value,
      weight_kg: calculationStore.massBalanceResult.takeoff_weight_kg,
      pressure_altitude_ft: pressureAltitude.value,
      temperature_c: temperature.value,
      wind_component_kt: windComponent.value,
      runway_condition: runwayCondition.value,
      runway_slope_percent: runwaySlope.value,
    })

    toast.add({
      severity: 'success',
      summary: 'Calculated',
      detail: 'Performance calculation complete',
      life: 3000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Performance calculation failed',
      life: 5000,
    })
  }
}
</script>

<template>
  <div class="calculation-view animate-fade-in">
    <header class="page-header">
      <h1 class="page-title">
        <span class="text-gradient">New Calculation</span>
      </h1>
      <p class="page-subtitle">Calculate Mass & Balance and Performance</p>
    </header>

    <div class="calculation-layout">
      <!-- Input Section -->
      <div class="input-section">
        <!-- Aircraft Selection -->
        <Card class="input-card">
          <template #title>Aircraft</template>
          <template #content>
            <Dropdown
              v-model="selectedAircraftId"
              :options="aircraftStore.aircraft"
              optionLabel="registration"
              optionValue="id"
              placeholder="Select Aircraft"
              class="w-full"
              @change="onAircraftChange"
            >
              <template #option="{ option }">
                <div>
                  <strong>{{ option.registration }}</strong>
                  <span class="option-sub"> - {{ option.manufacturer }} {{ option.aircraft_type }}</span>
                </div>
              </template>
            </Dropdown>
          </template>
        </Card>

        <!-- Weight Inputs -->
        <Card class="input-card" v-if="selectedAircraft">
          <template #title>Weights</template>
          <template #content>
            <div class="weight-inputs">
              <div v-if="aircraftStore.currentAircraft && weightInputs.length > 0">
                <LoadingStation
                  v-for="(station, index) in aircraftStore.currentAircraft.weight_stations"
                  :key="station.id"
                  :station="station"
                  v-model:weight="weightInputs[index].weight_kg"
                />
              </div>

              <Divider />

              <div class="weight-row">
                <label>Block Fuel</label>
                <InputNumber
                  v-model="fuelLiters"
                  suffix=" L"
                  :min="0"
                  :max="selectedAircraft.fuel_capacity_l"
                  class="weight-input"
                />
              </div>

              <div class="weight-row">
                <label>Trip Fuel</label>
                <InputNumber
                  v-model="tripFuelLiters"
                  suffix=" L"
                  :min="0"
                  :max="fuelLiters"
                  class="weight-input"
                />
              </div>
            </div>

            <Button
              label="Calculate M&B"
              icon="pi pi-calculator"
              class="p-button-primary w-full mt-3"
              :loading="calculationStore.loading"
              @click="calculateMassBalance"
            />
          </template>
        </Card>

        <!-- Performance Inputs -->
        <Card class="input-card" v-if="calculationStore.massBalanceResult">
          <template #title>Performance Conditions</template>
          <template #content>
            <div class="weight-inputs">
              <div class="weight-row">
                <label>Pressure Altitude</label>
                <InputNumber
                  v-model="pressureAltitude"
                  suffix=" ft"
                  class="weight-input"
                />
              </div>

              <div class="weight-row">
                <label>Temperature (OAT)</label>
                <InputNumber
                  v-model="temperature"
                  suffix=" °C"
                  class="weight-input"
                />
              </div>

              <div class="weight-row">
                <label>Wind Component</label>
                <InputNumber
                  v-model="windComponent"
                  suffix=" kt"
                  class="weight-input"
                />
                <small class="hint">Negative = Headwind</small>
              </div>

              <div class="weight-row">
                <label>Runway Condition</label>
                <Dropdown
                  v-model="runwayCondition"
                  :options="runwayConditions"
                  optionLabel="label"
                  optionValue="value"
                  class="weight-input"
                />
              </div>

              <div class="weight-row">
                <label>Runway Slope</label>
                <InputNumber
                  v-model="runwaySlope"
                  suffix=" %"
                  :min="-3"
                  :max="3"
                  :minFractionDigits="1"
                  class="weight-input"
                />
              </div>
            </div>

            <Button
              label="Calculate Performance"
              icon="pi pi-chart-line"
              class="p-button-secondary w-full mt-3"
              :loading="calculationStore.loading"
              @click="calculatePerformance"
            />
          </template>
        </Card>
      </div>

      <!-- Results Section -->
      <div class="results-section">
        <!-- M&B Results -->
        <Card class="result-card" v-if="calculationStore.massBalanceResult">
          <template #title>Mass & Balance Results</template>
          <template #content>
            <!-- Warnings -->
            <Message
              v-for="(warning, index) in calculationStore.massBalanceResult.warnings"
              :key="index"
              severity="warn"
              :closable="false"
            >
              {{ warning }}
            </Message>

            <!-- Weight Summary -->
            <div class="result-grid">
              <div class="result-item">
                <span class="result-label">Empty Weight</span>
                <span class="result-value">{{ calculationStore.massBalanceResult.empty_weight_kg }} kg</span>
              </div>
              <div class="result-item">
                <span class="result-label">Payload</span>
                <span class="result-value">{{ calculationStore.massBalanceResult.payload_kg }} kg</span>
              </div>
              <div class="result-item">
                <span class="result-label">Fuel Weight</span>
                <span class="result-value">{{ calculationStore.massBalanceResult.fuel_weight_kg }} kg</span>
              </div>
              <div class="result-item highlight">
                <span class="result-label">Takeoff Weight</span>
                <span class="result-value" :class="{ 'status-danger': !calculationStore.massBalanceResult.within_weight_limits }">
                  {{ calculationStore.massBalanceResult.takeoff_weight_kg }} kg
                </span>
              </div>
              <div class="result-item highlight">
                <span class="result-label">Landing Weight</span>
                <span class="result-value">{{ calculationStore.massBalanceResult.landing_weight_kg }} kg</span>
              </div>
            </div>

            <!-- CG Points -->
            <Divider />
            <h4>CG Positions</h4>
            <div class="cg-points">
              <div
                v-for="point in calculationStore.massBalanceResult.cg_points"
                :key="point.label"
                class="cg-point"
                :class="{ 'out-of-limits': !point.within_limits }"
              >
                <span class="cg-label">{{ point.label }}</span>
                <span class="cg-arm">{{ point.arm_m.toFixed(3) }} m</span>
                <i
                  :class="['pi', point.within_limits ? 'pi-check-circle status-success' : 'pi-times-circle status-danger']"
                ></i>
              </div>
            </div>

            <!-- Chart -->
            <div 
              v-if="aircraftStore.currentAircraft?.cg_envelopes?.length && calculationStore.massBalanceResult.cg_points" 
              class="chart-container"
            >
              <CGEnvelopeChart
                :envelope="aircraftStore.currentAircraft.cg_envelopes[0]"
                :points="calculationStore.massBalanceResult.cg_points"
              />
            </div>
            <!-- Fallback to static image if interactive not possible (legacy support) -->
            <div v-else-if="calculationStore.massBalanceResult.chart_image_base64" class="chart-container">
              <img
                :src="`data:image/png;base64,${calculationStore.massBalanceResult.chart_image_base64}`"
                alt="M&B Chart"
                class="mb-chart"
              />
            </div>
          </template>
        </Card>

        <!-- Performance Results -->
        <Card class="result-card" v-if="calculationStore.performanceResult">
          <template #title>Performance Results</template>
          <template #content>
            <!-- Warnings -->
            <Message
              v-for="(warning, index) in calculationStore.performanceResult.warnings"
              :key="index"
              severity="warn"
              :closable="false"
            >
              {{ warning }}
            </Message>

            <div class="result-grid">
              <div class="result-item">
                <span class="result-label">Takeoff Ground Roll</span>
                <span class="result-value">{{ calculationStore.performanceResult.takeoff_ground_roll_m }} m</span>
              </div>
              <div class="result-item">
                <span class="result-label">Takeoff Distance (50ft)</span>
                <span class="result-value">{{ calculationStore.performanceResult.takeoff_distance_50ft_m }} m</span>
              </div>
              <div class="result-item">
                <span class="result-label">Landing Ground Roll</span>
                <span class="result-value">{{ calculationStore.performanceResult.landing_ground_roll_m }} m</span>
              </div>
              <div class="result-item">
                <span class="result-label">Landing Distance (50ft)</span>
                <span class="result-value">{{ calculationStore.performanceResult.landing_distance_50ft_m }} m</span>
              </div>
            </div>

            <!-- Corrections Applied -->
            <Divider />
            <h4>Corrections Applied</h4>
            <ul class="corrections-list">
              <li v-for="(corr, index) in calculationStore.performanceResult.corrections_applied" :key="index">
                {{ corr }}
              </li>
            </ul>

            <small class="source-info">
              Source: {{ calculationStore.performanceResult.calculation_source }}
            </small>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calculation-view {
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

.calculation-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: var(--spacing-xl);
}

@media (max-width: 1024px) {
  .calculation-layout {
    grid-template-columns: 1fr;
  }
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.input-card :deep(.p-card-title) {
  font-size: var(--font-size-lg);
}

.weight-inputs {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.weight-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
}

.weight-row label {
  flex: 1;
  color: var(--color-text-secondary);
}

.weight-input {
  width: 150px;
}

.hint {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

.w-full {
  width: 100%;
}

.mt-3 {
  margin-top: var(--spacing-md);
}

.option-sub {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* Results */
.results-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.result-card :deep(.p-card-title) {
  font-size: var(--font-size-lg);
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--spacing-md);
}

.result-item {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

.result-item.highlight {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.result-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.result-value {
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.cg-points {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.cg-point {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

.cg-point.out-of-limits {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.cg-label {
  flex: 1;
  font-weight: 500;
}

.cg-arm {
  color: var(--color-text-secondary);
}

.chart-container {
  margin-top: var(--spacing-lg);
  text-align: center;
}

.mb-chart {
  max-width: 100%;
  border-radius: var(--radius-lg);
}

.corrections-list {
  margin: 0;
  padding-left: var(--spacing-lg);
  color: var(--color-text-secondary);
}

.corrections-list li {
  margin-bottom: var(--spacing-xs);
}

.source-info {
  display: block;
  margin-top: var(--spacing-md);
  color: var(--color-text-muted);
  text-transform: uppercase;
}
</style>
