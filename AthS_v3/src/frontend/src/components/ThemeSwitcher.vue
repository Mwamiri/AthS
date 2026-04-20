<script setup lang="ts">
import { useTheme, type Theme } from '@/composables/useTheme'

const { theme, setTheme, isDark, isOcean, isLight } = useTheme()

const themes: { id: Theme; label: string; icon: string }[] = [
  { id: 'light', label: 'Light', icon: '☀️' },
  { id: 'dark', label: 'Dark', icon: '🌙' },
  { id: 'ocean', label: 'Ocean', icon: '🌊' }
]
</script>

<template>
  <div class="flex items-center gap-2">
    <button
      v-for="t in themes"
      :key="t.id"
      @click="setTheme(t.id)"
      class="px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 active:scale-95"
      :class="[
        theme === t.id
          ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 shadow-md'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
      ]"
      :title="t.label"
    >
      <span class="text-lg">{{ t.icon }}</span>
    </button>
  </div>
</template>

<style scoped>
button {
  backdrop-filter: blur(4px);
}
</style>
