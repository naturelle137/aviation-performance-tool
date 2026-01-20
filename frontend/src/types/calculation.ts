/**
 * Calculation TypeScript type definitions
 */

export interface WeightInput {
    station_name: string
    weight_kg: number
}

export interface CGPoint {
    label: string
    weight_kg: number
    arm_m: number
    moment_kg_m: number
    within_limits: boolean
}

export interface MassBalanceRequest {
    aircraft_id: number
    weight_inputs: WeightInput[]
    fuel_liters: number
    trip_fuel_liters: number
}

export interface MassBalanceResponse {
    empty_weight_kg: number
    payload_kg: number
    fuel_weight_kg: number
    takeoff_weight_kg: number
    landing_weight_kg: number
    cg_points: CGPoint[]
    within_weight_limits: boolean
    within_cg_limits: boolean
    warnings: string[]
    chart_image_base64: string | null
}

export type RunwayCondition = 'dry' | 'wet' | 'grass'

export interface PerformanceRequest {
    aircraft_id: number
    weight_kg: number
    pressure_altitude_ft: number
    temperature_c: number
    wind_component_kt: number
    runway_condition: RunwayCondition
    runway_slope_percent: number
}

export interface PerformanceResponse {
    takeoff_ground_roll_m: number
    takeoff_distance_50ft_m: number
    landing_ground_roll_m: number
    landing_distance_50ft_m: number
    rate_of_climb_fpm: number | null
    corrections_applied: string[]
    calculation_source: string
    warnings: string[]
}
