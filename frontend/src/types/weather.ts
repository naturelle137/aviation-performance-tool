/**
 * Weather TypeScript type definitions
 */

export interface CloudLayer {
    cover: string
    height_ft: number
}

export interface MetarResponse {
    raw: string
    station: string
    time: string
    wind_direction: number | null
    wind_speed_kt: number
    wind_gust_kt: number | null
    visibility_m: number
    temperature_c: number
    dewpoint_c: number
    qnh_hpa: number
    clouds: CloudLayer[]
}

export interface TafResponse {
    raw: string
    station: string
    issued: string
    valid_from: string
    valid_to: string
    forecasts: Record<string, unknown>[]
}
