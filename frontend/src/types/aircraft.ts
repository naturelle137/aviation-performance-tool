/**
 * Aircraft TypeScript type definitions
 */

export interface WeightStation {
    id?: number
    name: string
    arm_m: number
    max_weight_kg: number | null
    default_weight_kg: number | null
    sort_order?: number
}

export interface CGEnvelopePoint {
    weight_kg: number
    arm_m: number
}

export interface CGEnvelope {
    id?: number
    category: 'normal' | 'utility' | 'acrobatic'
    polygon_points: CGEnvelopePoint[]
}

export interface FuelTank {
    id?: number
    name: string
    capacity_l: number
    arm_m: number
    unusable_fuel_l: number
    fuel_type: 'MoGas' | 'AvGas 100LL' | 'Jet A-1' | 'AvGas UL91' | 'Diesel'
    default_quantity_l: number
}

export interface Aircraft {
    id: number
    registration: string
    aircraft_type: string
    manufacturer: string
    empty_weight_kg: number
    empty_arm_m: number
    mtow_kg: number
    max_landing_weight_kg: number | null
    max_ramp_weight_kg: number | null
    fuel_capacity_l: number
    fuel_arm_m: number
    fuel_density_kg_l: number
    performance_source: 'fsm375' | 'manufacturer' | 'custom'
    weighing_date: string | null
    created_at: string
    updated_at: string
}

export interface AircraftWithDetails extends Aircraft {
    weight_stations: WeightStation[]
    cg_envelopes: CGEnvelope[]
    fuel_tanks: FuelTank[]
}

export interface AircraftCreate {
    registration: string
    aircraft_type: string
    manufacturer: string
    empty_weight_kg: number
    empty_arm_m: number
    mtow_kg: number
    max_landing_weight_kg?: number | null
    max_ramp_weight_kg?: number | null
    // Legacy fields used for form binding only, converted to fuel_tanks
    fuel_capacity_l: number
    fuel_arm_m: number
    fuel_density_kg_l?: number

    weight_stations?: WeightStation[]
    cg_envelopes?: CGEnvelope[]
    fuel_tanks?: Partial<FuelTank>[]
}

export interface AircraftUpdate {
    registration?: string
    aircraft_type?: string
    manufacturer?: string
    empty_weight_kg?: number
    empty_arm_m?: number
    mtow_kg?: number
    max_landing_weight_kg?: number | null
    max_ramp_weight_kg?: number | null
    fuel_capacity_l?: number
    fuel_arm_m?: number
    fuel_density_kg_l?: number
    fuel_tanks?: Partial<FuelTank>[]
}
