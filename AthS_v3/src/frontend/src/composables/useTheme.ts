import { ref, watch } from 'vue'

export type Theme = 'light' | 'dark' | 'ocean'

const THEME_KEY = 'aths-theme'

const theme = ref<Theme>(() => {
  const saved = localStorage.getItem(THEME_KEY)
  if (saved && ['light', 'dark', 'ocean'].includes(saved)) {
    return saved as Theme
  }
  return 'light'
}())

function applyTheme(newTheme: Theme): void {
  const html = document.documentElement
  
  html.classList.remove('dark', 'ocean-theme')
  
  if (newTheme === 'dark') {
    html.classList.add('dark')
  } else if (newTheme === 'ocean') {
    html.classList.add('ocean-theme')
  }
  
  localStorage.setItem(THEME_KEY, newTheme)
}

applyTheme(theme.value)

export function useTheme() {
  const setTheme = (newTheme: Theme): void => {
    theme.value = newTheme
    applyTheme(newTheme)
  }

  const toggleTheme = (): void => {
    const themes: Theme[] = ['light', 'dark', 'ocean']
    const currentIndex = themes.indexOf(theme.value)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }

  const isDark = ref(theme.value === 'dark')
  const isOcean = ref(theme.value === 'ocean')
  const isLight = ref(theme.value === 'light')

  watch(theme, (newTheme) => {
    isDark.value = newTheme === 'dark'
    isOcean.value = newTheme === 'ocean'
    isLight.value = newTheme === 'light'
  })

  return {
    theme,
    setTheme,
    toggleTheme,
    isDark,
    isOcean,
    isLight
  }
}
