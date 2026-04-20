<script setup lang="ts">
import { ref, computed } from 'vue'
import { LineChart, registerables } from 'chart.js'
import { Line } from 'vue-chartjs'
import type { ChartData, ChartOptions } from 'chart.js'

LineChart.register(...registerables)

interface DataPoint {
  label: string
  value: number
}

const props = defineProps<{
  title?: string
  data: DataPoint[]
  color?: string
}>()

const chartRef = ref<typeof Line | null>(null)

const chartData = computed<ChartData<'line'>>(() => ({
  labels: props.data.map(d => d.label),
  datasets: [
    {
      label: 'Performance',
      data: props.data.map(d => d.value),
      borderColor: props.color || '#3b82f6',
      backgroundColor: props.color ? `${props.color}20` : 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true,
      pointRadius: 4,
      pointHoverRadius: 6,
      pointBackgroundColor: props.color || '#3b82f6',
      pointBorderColor: '#fff',
      pointBorderWidth: 2
    }
  ]
}))

const chartOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      padding: 12,
      cornerRadius: 8,
      displayColors: false,
      callbacks: {
        label: (context) => `Value: ${context.parsed.y}`
      }
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: '#9ca3af'
      }
    },
    y: {
      grid: {
        color: 'rgba(156, 163, 175, 0.2)'
      },
      ticks: {
        color: '#9ca3af'
      },
      beginAtZero: true
    }
  }
}))
</script>

<template>
  <div class="h-full w-full">
    <Line
      v-if="chartRef"
      ref="chartRef"
      :data="chartData"
      :options="chartOptions"
    />
    <Line
      v-else
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<style scoped>
canvas {
  max-height: 100%;
}
</style>
