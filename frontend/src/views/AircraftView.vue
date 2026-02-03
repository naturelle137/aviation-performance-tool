<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAircraftStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import type { AircraftCreate } from '@/types'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()
const aircraftStore = useAircraftStore()

const showAddDialog = ref(false)
const formData = ref<AircraftCreate>({
  registration: '',
  aircraft_type: '',
  manufacturer: '',
  empty_weight_kg: 0,
  empty_arm_m: 0,
  mtow_kg: 0,
  fuel_capacity_l: 0,
  fuel_arm_m: 0,
  fuel_density_kg_l: 0.72,
})

onMounted(async () => {
  await aircraftStore.fetchAll()
})

function openAddDialog(): void {
  formData.value = {
    registration: '',
    aircraft_type: '',
    manufacturer: '',
    empty_weight_kg: 0,
    empty_arm_m: 0,
    mtow_kg: 0,
    fuel_capacity_l: 0,
    fuel_arm_m: 0,
    fuel_density_kg_l: 0.72,
  }
  showAddDialog.value = true
}

async function saveAircraft(): Promise<void> {
  try {
    // Transform legacy flat fuel data to fuel_tanks array
    const payload = {
      ...formData.value,
      fuel_tanks: [
        {
          name: 'Main Tank',
          capacity_l: formData.value.fuel_capacity_l,
          arm_m: formData.value.fuel_arm_m,
          unusable_fuel_l: 0,
          fuel_type: 'AvGas 100LL' as const,
          default_quantity_l: formData.value.fuel_capacity_l,
        },
      ],
    }
    // Remove legacy fields from payload to avoid confusion (backend ignores them anyway)
    // delete payload.fuel_capacity_l
    // delete payload.fuel_arm_m

    await aircraftStore.create(payload)
    showAddDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Aircraft ${formData.value.registration} created`,
      life: 3000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to create aircraft',
      life: 5000,
    })
  }
}

function confirmDelete(id: number, registration: string): void {
  confirm.require({
    message: `Are you sure you want to delete ${registration}?`,
    header: 'Delete Confirmation',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await aircraftStore.remove(id)
        toast.add({
          severity: 'success',
          summary: 'Deleted',
          detail: `Aircraft ${registration} deleted`,
          life: 3000,
        })
      } catch {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete aircraft',
          life: 5000,
        })
      }
    },
  })
}
</script>

<template>
  <div class="aircraft-view animate-fade-in">
    <header class="page-header">
      <div>
        <h1 class="page-title">
          <span class="text-gradient">Aircraft Fleet</span>
        </h1>
        <p class="page-subtitle">Manage your registered aircraft</p>
      </div>
      <Button
        icon="pi pi-plus"
        label="Add Aircraft"
        class="p-button-primary"
        @click="openAddDialog"
      />
    </header>

    <!-- Aircraft Table -->
    <div class="card">
      <DataTable
        :value="aircraftStore.aircraft"
        :loading="aircraftStore.loading"
        stripedRows
        responsiveLayout="scroll"
        class="aircraft-table"
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-inbox empty-icon"></i>
            <p>No aircraft registered yet</p>
            <Button label="Add your first aircraft" @click="openAddDialog" />
          </div>
        </template>

        <Column field="registration" header="Registration" sortable>
          <template #body="{ data }">
            <span class="registration-link" @click="router.push(`/aircraft/${data.id}`)">
              {{ data.registration }}
            </span>
          </template>
        </Column>
        <Column field="aircraft_type" header="Type" sortable />
        <Column field="manufacturer" header="Manufacturer" sortable />
        <Column field="mtow_kg" header="MTOW (kg)" sortable>
          <template #body="{ data }">
            {{ data.mtow_kg.toLocaleString() }}
          </template>
        </Column>
        <Column field="fuel_capacity_l" header="Fuel (L)" sortable />
        <Column header="Actions" style="width: 150px">
          <template #body="{ data }">
            <div class="action-buttons">
              <Button
                icon="pi pi-eye"
                class="p-button-text p-button-sm"
                @click="router.push(`/aircraft/${data.id}`)"
              />
              <Button
                icon="pi pi-trash"
                class="p-button-text p-button-danger p-button-sm"
                @click="confirmDelete(data.id, data.registration)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Add Aircraft Dialog -->
    <Dialog
      v-model:visible="showAddDialog"
      header="Add New Aircraft"
      :modal="true"
      :style="{ width: '600px' }"
    >
      <div class="form-grid">
        <div class="form-field">
          <label for="registration">Registration *</label>
          <InputText
            id="registration"
            v-model="formData.registration"
            placeholder="D-EABC"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="manufacturer">Manufacturer *</label>
          <InputText
            id="manufacturer"
            v-model="formData.manufacturer"
            placeholder="Cessna"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="type">Type *</label>
          <InputText
            id="type"
            v-model="formData.aircraft_type"
            placeholder="C172S"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="mtow">MTOW (kg) *</label>
          <InputNumber
            id="mtow"
            v-model="formData.mtow_kg"
            :min="0"
            :max="10000"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="empty_weight">Empty Weight (kg) *</label>
          <InputNumber
            id="empty_weight"
            v-model="formData.empty_weight_kg"
            :min="0"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="empty_arm">Empty Arm (m) *</label>
          <InputNumber
            id="empty_arm"
            v-model="formData.empty_arm_m"
            :minFractionDigits="2"
            :maxFractionDigits="3"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="fuel_capacity">Fuel Capacity (L) *</label>
          <InputNumber
            id="fuel_capacity"
            v-model="formData.fuel_capacity_l"
            :min="0"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="fuel_arm">Fuel Arm (m) *</label>
          <InputNumber
            id="fuel_arm"
            v-model="formData.fuel_arm_m"
            :minFractionDigits="2"
            :maxFractionDigits="3"
            class="w-full"
          />
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showAddDialog = false" />
        <Button label="Save" class="p-button-primary" @click="saveAircraft" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.aircraft-view {
  padding-bottom: var(--spacing-2xl);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-xs);
}

.page-subtitle {
  color: var(--color-text-secondary);
}

.registration-link {
  color: var(--color-accent-primary);
  font-weight: 600;
  cursor: pointer;
}

.registration-link:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-field label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.w-full {
  width: 100%;
}
</style>
