/**
 * Weather API service
 */

import api from './api'
import type { MetarResponse, TafResponse } from '@/types'

const BASE_PATH = '/api/v1/weather'

export const weatherService = {
    /**
     * Get METAR for an airport
     */
    async getMetar(icao: string): Promise<MetarResponse> {
        const response = await api.get<MetarResponse>(`${BASE_PATH}/metar/${icao.toUpperCase()}`)
        return response.data
    },

    /**
     * Get TAF for an airport
     */
    async getTaf(icao: string): Promise<TafResponse> {
        const response = await api.get<TafResponse>(`${BASE_PATH}/taf/${icao.toUpperCase()}`)
        return response.data
    },
}
