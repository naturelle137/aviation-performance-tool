<script setup lang="ts">
/**
 * Interactive CG Envelope Chart.
 * Implements:
 * - REQ-MB-02: Real-time CG envelope display.
 * - REQ-MB-09: Render dynamic CG points and limits.
 */
import { computed } from 'vue'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions
} from 'chart.js'
import { Scatter } from 'vue-chartjs'
import type { CGEnvelope, CGPoint } from '@/types'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend)

const props = defineProps<{
  envelope: CGEnvelope
  points: CGPoint[]
}>()

const chartData = computed<ChartData<'scatter'>>(() => {
  // 1. Envelope Polygon (Line)
  // Close the loop by repeating the first point at the end
  const envelopePoints = props.envelope.polygon_points.map(p => ({
    x: p.arm_m,
    y: p.weight_kg
  }))
  
  if (envelopePoints.length > 0) {
    envelopePoints.push(envelopePoints[0])
  }

  // 2. CG Points (Scatter)
  // Map our specific points (ZFW, TOW, LDG)
  const scatterPoints = props.points.map(p => ({
    x: p.arm_m,
    y: p.weight_kg,
    label: p.label
  }))

  return {
    datasets: [
      {
        label: 'CG Envelope',
        data: envelopePoints,
        borderColor: 'rgb(59, 130, 246)', // Blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        showLine: true,
        fill: true,
        pointRadius: 0,
        tension: 0,
        order: 2
      },
      {
        label: 'Loading Points',
        data: scatterPoints,
        backgroundColor: (context) => {
            const index = context.dataIndex;
            const pointRaw = props.points[index];
            return pointRaw?.within_limits ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'; // Green/Red
        },
        borderColor: '#fff',
        pointRadius: 6,
        pointHoverRadius: 8,
        order: 1
      },
      // Draw lines between points to show migration if we have standard points
      // This is a bit tricky in Chart.js mixed mode, simpliest is just scatter for points now.
    ]
  }
})

const chartOptions = computed<ChartOptions<'scatter'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'linear',
      position: 'bottom',
      title: {
        display: true,
        text: 'Center of Gravity (Arm) [m]',
        color: '#94a3b8'
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      },
      ticks: {
        color: '#94a3b8'
      }
    },
    y: {
      type: 'linear',
      title: {
        display: true,
        text: 'Weight [kg]',
        color: '#94a3b8'
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      },
      ticks: {
        color: '#94a3b8'
      }
    }
  },
  plugins: {
    legend: {
      labels: {
        color: '#e2e8f0'
      }
    },
    tooltip: {
        callbacks: {
            label: (context) => {
                const point = context.raw as { x: number, y: number, label?: string };
                // If it's the envelope, just show coordinates
                if (context.datasetIndex === 0) {
                    return `Envelope: ${point.x.toFixed(3)}m / ${point.y}kg`;
                }
                // If it's a point, show label
                const label = point.label || 'Point';
                return `${label}: ${point.y}kg @ ${point.x.toFixed(3)}m`;
            }
        }
    }
  }
}))
</script>

<template>
  <div class="chart-wrapper">
    <Scatter :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 400px;
}
</style>
