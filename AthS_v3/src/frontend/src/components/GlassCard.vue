<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface MousePosition {
  x: number
  y: number
}

const props = defineProps<{
  title?: string
  subtitle?: string
  hoverGlow?: boolean
}>()

const cardRef = ref<HTMLElement | null>(null)
const mousePosition = ref<MousePosition>({ x: 0, y: 0 })
const isHovering = ref(false)

function handleMouseMove(e: MouseEvent): void {
  if (!cardRef.value) return
  
  const rect = cardRef.value.getBoundingClientRect()
  mousePosition.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
}

function handleMouseEnter(): void {
  isHovering.value = true
}

function handleMouseLeave(): void {
  isHovering.value = false
}

onMounted(() => {
  if (cardRef.value && props.hoverGlow) {
    cardRef.value.addEventListener('mousemove', handleMouseMove)
    cardRef.value.addEventListener('mouseenter', handleMouseEnter)
    cardRef.value.addEventListener('mouseleave', handleMouseLeave)
  }
})

onUnmounted(() => {
  if (cardRef.value && props.hoverGlow) {
    cardRef.value.removeEventListener('mousemove', handleMouseMove)
    cardRef.value.removeEventListener('mouseenter', handleMouseEnter)
    cardRef.value.removeEventListener('mouseleave', handleMouseLeave)
  }
})
</script>

<template>
  <div
    ref="cardRef"
    class="glass-card p-6 relative overflow-hidden transition-all duration-300"
    :class="{
      'hover:shadow-2xl hover:-translate-y-1': hoverGlow !== false,
      'cursor-default': !hoverGlow
    }"
    :style="hoverGlow && isHovering ? {
      background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.1), transparent 40%)`
    } : {}"
  >
    <slot name="header">
      <div v-if="title || subtitle" class="mb-4">
        <h3 v-if="title" class="text-xl font-semibold text-gray-900 dark:text-white">
          {{ title }}
        </h3>
        <p v-if="subtitle" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ subtitle }}
        </p>
      </div>
    </slot>
    
    <slot />
  </div>
</template>

<style scoped>
.glass-card {
  backdrop-filter: blur(10px);
}
</style>
