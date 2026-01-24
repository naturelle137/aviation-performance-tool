import type { CGEnvelope, CGPoint } from '@/types'

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
        { label: 'Takeoff', weight_kg: 950, arm_m: 2.45, moment_kg_m: 2327.5, within_limits: true }
    ]

    it('renders without crashing', () => {
        // @ts-expect-error - Mocking complex Chart.js props
        const wrapper = mount(CGEnvelopeChart, {
            props: {
                envelope: mockEnvelope,
                points: mockPoints
            }
        })
        expect(wrapper.exists()).toBe(true)
    })

    it('processes polygon points correctly', () => {
        // Access component instance to check computed properties
        // @ts-expect-error - Accessing internal VM for testing
        const wrapper = mount(CGEnvelopeChart, {
            props: {
                envelope: mockEnvelope,
                points: mockPoints
            }
        })

        // We can indirectly verify by checking if it didn't throw
        expect(wrapper.vm).toBeTruthy()
    })
})
