import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingStation from '../LoadingStation.vue'
import PrimeVue from 'primevue/config'

describe('LoadingStation', () => {
    const mockStation = {
        id: 1,
        name: 'Front Seats',
        arm_m: 2.30,
        max_weight_kg: 200,
        default_weight_kg: 80,
        sort_order: 1
    }

    it('renders properly', () => {
        const wrapper = mount(LoadingStation, {
            props: {
                station: mockStation,
                weight: 80
            },
            global: {
                plugins: [PrimeVue],
                stubs: ['InputNumber']
            }
        })

        expect(wrapper.text()).toContain('Front Seats')
        expect(wrapper.text()).toContain('Arm: 2.300 m')
        expect(wrapper.text()).toContain('Max: 200 kg')
    })

    it('shows danger class when overweight', () => {
        const wrapper = mount(LoadingStation, {
            props: {
                station: mockStation,
                weight: 250 // Over 200 limit
            },
            global: {
                plugins: [PrimeVue],
                stubs: ['InputNumber']
            }
        })

        const maxLabel = wrapper.find('.max-weight')
        expect(maxLabel.classes()).toContain('text-danger')
    })

    it('handles infinite capacity', () => {
        const infiniteStation = { ...mockStation, max_weight_kg: null }
        const wrapper = mount(LoadingStation, {
            props: {
                station: infiniteStation,
                weight: 500
            },
            global: {
                plugins: [PrimeVue],
                stubs: ['InputNumber']
            }
        })

        expect(wrapper.text()).toContain('No limit')
    })
})
