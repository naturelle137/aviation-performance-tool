/**
 * Axios API client configuration
 */

import axios, { type AxiosInstance, type AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Add auth token if available (for future OAuth)
        const token = localStorage.getItem('auth_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        // Handle common errors
        if (error.response?.status === 401) {
            // Unauthorized - redirect to login (future)
            localStorage.removeItem('auth_token')
        }

        // Log error for debugging
        console.error('API Error:', {
            url: error.config?.url,
            status: error.response?.status,
            message: error.message,
        })

        return Promise.reject(error)
    }
)

export default api
