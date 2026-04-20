<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  targetValue: number
  duration?: number
  prefix?: string
  suffix?: string
}>()

const currentValue = ref(0)
const displayValue = ref('0')

function formatNumber(value: number): string {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toFixed(0)
}

function animate(): void {
  const startTime = performance.now()
  const duration = props.duration || 2000
  const startValue = 0
  const endValue = props.targetValue

  function update(currentTime: number): void {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // Easing function (ease-out-cubic)
    const easedProgress = 1 - Math.pow(1 - progress, 3)
    
    currentValue.value = startValue + (endValue - startValue) * easedProgress
    displayValue.value = formatNumber(currentValue.value)

    if (progress < 1) {
      requestAnimationFrame(update)
    } else {
      currentValue.value = endValue
      displayValue.value = formatNumber(endValue)
    }
  }

  requestAnimationFrame(update)
}

onMounted(() => {
  animate()
})
</script>

<template>
  <span class="inline-block tabular-nums">
    {{ prefix }}{{ displayValue }}{{ suffix }}
  </span>
</template>

<style scoped>
span {
  font-variant-numeric: tabular-nums;
}
</style>
