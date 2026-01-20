/**
 * Calculation API service
 */

import api from './api'
import type {
    MassBalanceRequest,
    MassBalanceResponse,
    PerformanceRequest,
    PerformanceResponse,
} from '@/types'

const BASE_PATH = '/api/v1/calculations'

export const calculationService = {
    /**
     * Calculate mass and balance
     */
    async calculateMassBalance(data: MassBalanceRequest): Promise<MassBalanceResponse> {
        const response = await api.post<MassBalanceResponse>(`${BASE_PATH}/mass-balance`, data)
        return response.data
    },

    /**
     * Calculate takeoff/landing performance
     */
    async calculatePerformance(data: PerformanceRequest): Promise<PerformanceResponse> {
        const response = await api.post<PerformanceResponse>(`${BASE_PATH}/performance`, data)
        return response.data
    },
}
