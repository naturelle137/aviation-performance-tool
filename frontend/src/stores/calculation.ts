/**
 * Calculation Pinia store
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { calculationService } from '@/services'
import type {
    MassBalanceRequest,
    MassBalanceResponse,
    PerformanceRequest,
    PerformanceResponse,
} from '@/types'

export const useCalculationStore = defineStore('calculation', () => {
    // State
    const massBalanceResult = ref<MassBalanceResponse | null>(null)
    const performanceResult = ref<PerformanceResponse | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)

    // Actions
    async function calculateMassBalance(data: MassBalanceRequest): Promise<MassBalanceResponse> {
        loading.value = true
        error.value = null
        try {
            massBalanceResult.value = await calculationService.calculateMassBalance(data)
            return massBalanceResult.value
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to calculate mass balance'
            throw e
        } finally {
            loading.value = false
        }
    }

    async function calculatePerformance(data: PerformanceRequest): Promise<PerformanceResponse> {
        loading.value = true
        error.value = null
        try {
            performanceResult.value = await calculationService.calculatePerformance(data)
            return performanceResult.value
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to calculate performance'
            throw e
        } finally {
            loading.value = false
        }
    }

    function clearResults(): void {
        massBalanceResult.value = null
        performanceResult.value = null
        error.value = null
    }

    return {
        // State
        massBalanceResult,
        performanceResult,
        loading,
        error,
        // Actions
        calculateMassBalance,
        calculatePerformance,
        clearResults,
    }
})
