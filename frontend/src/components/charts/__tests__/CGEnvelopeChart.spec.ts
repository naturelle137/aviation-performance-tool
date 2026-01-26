import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CGEnvelopeChart from '../CGEnvelopeChart.vue'
import type { CGEnvelope, CGPoint } from '@/types'
import {
    Chart as ChartJS,
    Tooltip,
    type ChartData,
    type ChartOptions
} from 'chart.js'

// Mock Chart.js to prevent canvas errors in jsdom
vi.mock('vue-chartjs', () => ({
    Scatter: {
        template: '<div>Mock Chart</div>',
        props: ['data', 'options']
    }
}))

describe('CGEnvelopeChart', () => {
    const mockEnvelope: CGEnvelope = {
        category: 'normal',
        polygon_points: [
            { weight_kg: 900, arm_m: 2.4 },
            { weight_kg: 1000, arm_m: 2.5 },
            { weight_kg: 900, arm_m: 2.6 }
        ]
    }

    const mockPoints: CGPoint[] = [
        { label: 'Takeoff', weight_kg: 950, arm_m: 2.45, moment_kg_m: 2327.5, within_limits: true },
        { label: 'Landing', weight_kg: 850, arm_m: 2.55, moment_kg_m: 2167.5, within_limits: false }
    ]

    it('renders without crashing', () => {
        const wrapper = mount(CGEnvelopeChart, {
            props: {
                envelope: mockEnvelope,
                points: mockPoints
            }
        })
        expect(wrapper.exists()).toBe(true)
    })

    it('computes chart data correctly', () => {
        const wrapper = mount(CGEnvelopeChart, {
            props: {
                envelope: mockEnvelope,
                points: mockPoints
            }
        })

        // Access internal component instance to check computed properties
        const vm = wrapper.vm as any
        const chartData = vm.chartData as ChartData<'scatter'>

        // 1. Envelope dataset
        expect(chartData.datasets[0].label).toBe('CG Envelope')
        expect(chartData.datasets[0].data.length).toBe(4) // 3 points + 1 closure point

        // 2. Points dataset
        expect(chartData.datasets[1].label).toBe('Loading Points')
        expect(chartData.datasets[1].data.length).toBe(2)
    })

    it('computes point colors correctly', () => {
        const wrapper = mount(CGEnvelopeChart, {
            props: {
                envelope: mockEnvelope,
                points: mockPoints
            }
        })
        const vm = wrapper.vm as any
        const chartData = vm.chartData as ChartData<'scatter'>
        const bgCallback = chartData.datasets[1].backgroundColor as Function

        // Point 0: Takeoff (within limits) -> Green
        const context0 = { dataIndex: 0 }
        expect(bgCallback(context0)).toBe('rgb(34, 197, 94)')

        // Point 1: Landing (out of limits) -> Red
        const context1 = { dataIndex: 1 }
        expect(bgCallback(context1)).toBe('rgb(239, 68, 68)')
    })

    it('formats tooltips correctly', () => {
        const wrapper = mount(CGEnvelopeChart, {
            props: {
                envelope: mockEnvelope,
                points: mockPoints
            }
        })
        const vm = wrapper.vm as any
        const chartOptions = vm.chartOptions as ChartOptions<'scatter'>
        const labelCallback = chartOptions.plugins?.tooltip?.callbacks?.label as Function

        // 1. Envelope Tooltip
        const envContext = {
            datasetIndex: 0,
            raw: { x: 2.4, y: 900 }
        }
        expect(labelCallback(envContext)).toBe('Envelope: 2.400m / 900kg')

        // 2. Point Tooltip
        const pointContext = {
            datasetIndex: 1,
            raw: { x: 2.45, y: 950, label: 'Takeoff' }
        }
        expect(labelCallback(pointContext)).toBe('Takeoff: 950kg @ 2.450m')
    })
})
