/**
 * Aircraft API service
 */

import api from './api'
import type { Aircraft, AircraftWithDetails, AircraftCreate, AircraftUpdate } from '@/types'

const BASE_PATH = '/api/v1/aircraft'

export const aircraftService = {
    /**
     * Get all aircraft
     */
    async getAll(): Promise<Aircraft[]> {
        const response = await api.get<Aircraft[]>(BASE_PATH)
        return response.data
    },

    /**
     * Get aircraft by ID with full details
     */
    async getById(id: number): Promise<AircraftWithDetails> {
        const response = await api.get<AircraftWithDetails>(`${BASE_PATH}/${id}`)
        return response.data
    },

    /**
     * Create a new aircraft
     */
    async create(data: AircraftCreate): Promise<Aircraft> {
        const response = await api.post<Aircraft>(BASE_PATH, data)
        return response.data
    },

    /**
     * Update an existing aircraft
     */
    async update(id: number, data: AircraftUpdate): Promise<Aircraft> {
        const response = await api.put<Aircraft>(`${BASE_PATH}/${id}`, data)
        return response.data
    },

    /**
     * Delete an aircraft
     */
    async delete(id: number): Promise<void> {
        await api.delete(`${BASE_PATH}/${id}`)
    },
}
