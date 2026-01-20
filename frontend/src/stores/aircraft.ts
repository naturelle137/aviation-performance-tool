/**
 * Aircraft Pinia store
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { aircraftService } from '@/services'
import type { Aircraft, AircraftWithDetails, AircraftCreate, AircraftUpdate } from '@/types'

export const useAircraftStore = defineStore('aircraft', () => {
    // State
    const aircraft = ref<Aircraft[]>([])
    const currentAircraft = ref<AircraftWithDetails | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)

    // Getters
    const aircraftCount = computed(() => aircraft.value.length)

    const getAircraftById = computed(() => {
        return (id: number) => aircraft.value.find((a) => a.id === id)
    })

    // Actions
    async function fetchAll(): Promise<void> {
        loading.value = true
        error.value = null
        try {
            aircraft.value = await aircraftService.getAll()
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to fetch aircraft'
            throw e
        } finally {
            loading.value = false
        }
    }

    async function fetchById(id: number): Promise<AircraftWithDetails> {
        loading.value = true
        error.value = null
        try {
            currentAircraft.value = await aircraftService.getById(id)
            return currentAircraft.value
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to fetch aircraft'
            throw e
        } finally {
            loading.value = false
        }
    }

    async function create(data: AircraftCreate): Promise<Aircraft> {
        loading.value = true
        error.value = null
        try {
            const newAircraft = await aircraftService.create(data)
            aircraft.value.push(newAircraft)
            return newAircraft
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to create aircraft'
            throw e
        } finally {
            loading.value = false
        }
    }

    async function update(id: number, data: AircraftUpdate): Promise<Aircraft> {
        loading.value = true
        error.value = null
        try {
            const updated = await aircraftService.update(id, data)
            const index = aircraft.value.findIndex((a) => a.id === id)
            if (index !== -1) {
                aircraft.value[index] = updated
            }
            return updated
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to update aircraft'
            throw e
        } finally {
            loading.value = false
        }
    }

    async function remove(id: number): Promise<void> {
        loading.value = true
        error.value = null
        try {
            await aircraftService.delete(id)
            aircraft.value = aircraft.value.filter((a) => a.id !== id)
            if (currentAircraft.value?.id === id) {
                currentAircraft.value = null
            }
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to delete aircraft'
            throw e
        } finally {
            loading.value = false
        }
    }

    function clearCurrent(): void {
        currentAircraft.value = null
    }

    return {
        // State
        aircraft,
        currentAircraft,
        loading,
        error,
        // Getters
        aircraftCount,
        getAircraftById,
        // Actions
        fetchAll,
        fetchById,
        create,
        update,
        remove,
        clearCurrent,
    }
})
