import { createApp } from 'vue'
import { VueQueryPlugin } from '@tanstack/vue-query'
import App from './App.vue'
import router from './router'
import './assets/theme.css'

const app = createApp(App)

app.use(VueQueryPlugin)
app.use(router)

app.mount('#app')
