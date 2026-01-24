<script setup lang="ts">
import InputNumber from 'primevue/inputnumber'
import type { WeightStation } from '@/types'

const props = defineProps<{
  station: WeightStation
}>()

const weight = defineModel<number>('weight', { required: true })

// Helper to check max weight
const isOverweight = (val: number) => {
  return props.station.max_weight_kg && val > props.station.max_weight_kg
}
</script>

<template>
  <div class="loading-station">
    <div class="station-header">
      <label :for="`station-${station.id}`" class="station-label">
        {{ station.name }}
      </label>
      <span class="station-arm">Arm: {{ station.arm_m.toFixed(3) }} m</span>
    </div>
    
    <div class="input-wrapper">
      <InputNumber
        :id="`station-${station.id}`"
        v-model="weight"
        suffix=" kg"
        :min="0"
        :max="station.max_weight_kg || undefined"
        :class="{ 'p-invalid': isOverweight(weight) }"
        class="w-full"
        placeholder="0"
      />
    </div>
    
    <div class="station-footer">
      <small v-if="station.max_weight_kg" class="max-weight" :class="{ 'text-danger': isOverweight(weight) }">
        Max: {{ station.max_weight_kg }} kg
      </small>
      <small v-else class="text-muted">No limit</small>
    </div>
  </div>
</template>

<style scoped>
.loading-station {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.loading-station:focus-within {
  border-color: var(--color-accent-primary);
  background: rgba(255, 255, 255, 0.05);
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.station-label {
  font-weight: 500;
  color: var(--color-text-primary);
}

.station-arm {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.station-footer {
  display: flex;
  justify-content: flex-end;
}

.max-weight {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.text-danger {
  color: var(--color-accent-danger);
}

.text-muted {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}
</style>
