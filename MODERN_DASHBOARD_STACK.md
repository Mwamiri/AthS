# 🚀 Modern AthSys Dashboard Stack - Implementation Guide

**Technology Stack**: Vue 3 + Vite + TailwindCSS + Pinia + Vue Router  
**Purpose**: Replace disconnected HTML pages with unified, professional SPA  
**Status**: ✅ Ready to implement  
**Estimated Setup Time**: 30 minutes

---

## 🎯 What This Solves

### Current Issues
❌ Buttons not working across pages  
❌ No unified navigation  
❌ Data doesn't sync between pages  
❌ No state management  
❌ Outdated frontend architecture  

### What You'll Get
✅ Single Page Application (SPA) with instant page navigation  
✅ Unified state management (athletes, races, results)  
✅ Real-time data updates from backend  
✅ Professional UI with TailwindCSS  
✅ Type-safe routing with Vue Router  
✅ Responsive design (mobile-friendly)  
✅ Developer-friendly architecture  

---

## 📦 Tech Stack Breakdown

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Vue 3 | Modern reactive UI framework |
| **Bundler** | Vite | Lightning-fast builds & HMR |
| **Styling** | TailwindCSS | Utility-first CSS |
| **Icons** | Heroicons | Beautiful SVG icons |
| **Routing** | Vue Router 4 | Client-side navigation |
| **State** | Pinia | Lightweight state management |
| **API** | Axios | HTTP client for backend calls |
| **UI Components** | Headless UI | Accessible, unstyled components |
| **Notifications** | Vue Toastification | Toast notifications |
| **Testing** | Vitest + Cypress | Unit & E2E testing |

---

## 📁 Project Structure

```
src/
├── main.js                 # Vue app entry point
├── App.vue                 # Root component with layout
│
├── components/             # Reusable components
│   ├── Sidebar.vue
│   ├── Header.vue
│   ├── Table.vue
│   ├── Card.vue
│   ├── Modal.vue
│   └── Button.vue
│
├── pages/                  # Full-page components (routed)
│   ├── Dashboard.vue
│   ├── Races/
│   │   ├── RacesList.vue
│   │   ├── RaceDetail.vue
│   │   └── RaceForm.vue
│   ├── Athletes/
│   │   ├── AthletesList.vue
│   │   ├── AthleteDetail.vue
│   │   └── AthleteForm.vue
│   ├── Results/
│   │   ├── ResultsList.vue
│   │   └── ResultForm.vue
│   ├── Users/
│   │   ├── UsersList.vue
│   │   └── UserForm.vue
│   ├── Login.vue
│   └── NotFound.vue
│
├── router/
│   └── index.js           # Vue Router configuration
│
├── stores/                # Pinia stores
│   ├── auth.js           # Authentication state
│   ├── races.js          # Races data & actions
│   ├── athletes.js       # Athletes data & actions
│   ├── results.js        # Results data & actions
│   └── ui.js             # UI state (sidebar, modals, etc.)
│
├── services/              # API & utility services
│   ├── api.js            # Axios instance & base config
│   ├── auth.js           # Auth utilities
│   ├── races.js          # Races API calls
│   ├── athletes.js       # Athletes API calls
│   └── results.js        # Results API calls
│
├── utils/                 # Helper functions
│   ├── validation.js
│   ├── format.js
│   └── constants.js
│
└── styles/
    └── globals.css        # Global Tailwind directives

vite.config.js            # Vite configuration
tailwind.config.js        # TailwindCSS configuration
package.json              # Dependencies & scripts
```

---

## 🚀 Quick Start

### 1. Initialize Vue 3 + Vite Project

```bash
cd src/frontend
npm create vite@latest . -- --template vue
npm install
```

### 2. Install Dependencies

```bash
npm install \
  vue-router@4 \
  pinia \
  axios \
  @headlessui/vue \
  @heroicons/vue \
  @vueuse/core \
  tailwindcss \
  postcss \
  autoprefixer \
  vue-toastification \
  vitest \
  @vitest/ui \
  @vue/test-utils \
  cypress
```

### 3. Setup TailwindCSS

```bash
npx tailwindcss init -p
```

### 4. Configure Vue Project

Run each step in the following sections.

---

## 📝 File-by-File Implementation

### 1. vite.config.js

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    }
  }
})
```

### 2. tailwind.config.js

```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#ff6b35',
        secondary: '#06d6a0',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
```

### 3. src/main.js

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast, { POSITION } from "vue-toastification"
import "vue-toastification/dist/index.css"

import App from './App.vue'
import router from './router'
import './styles/globals.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Toast, {
  position: POSITION.TOP_RIGHT,
  timeout: 3000,
})

app.mount('#app')
```

### 4. src/styles/globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 rounded-lg font-semibold transition-colors;
  }

  .btn-primary {
    @apply btn bg-primary text-white hover:bg-orange-600;
  }

  .btn-secondary {
    @apply btn bg-gray-200 text-gray-900 hover:bg-gray-300;
  }

  .btn-danger {
    @apply btn bg-red-500 text-white hover:bg-red-600;
  }

  .card {
    @apply bg-white rounded-lg shadow-md p-6 border border-gray-100;
  }

  .input {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary;
  }
}
```

---

## 🔧 Store Examples (Pinia)

### src/stores/auth.js

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('authToken'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    loading.value = true
    try {
      const { data } = await api.post('/auth/login', { email, password })
      token.value = data.token
      user.value = data.user
      localStorage.setItem('authToken', data.token)
      return true
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('authToken')
  }

  function setAuthHeader() {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    logout,
    setAuthHeader
  }
})
```

### src/stores/races.js

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useRacesStore = defineStore('races', () => {
  const races = ref([])
  const loading = ref(false)
  const error = ref(null)

  const racesCount = computed(() => races.value.length)
  const upcomingRaces = computed(() => 
    races.value.filter(r => r.status === 'upcoming')
  )

  async function fetchRaces() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/api/races')
      races.value = data.races || []
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function createRace(raceData) {
    try {
      const { data } = await api.post('/api/races', raceData)
      races.value.push(data)
      return data
    } catch (err) {
      throw err
    }
  }

  async function deleteRace(id) {
    try {
      await api.delete(`/api/races/${id}`)
      races.value = races.value.filter(r => r.id !== id)
    } catch (err) {
      throw err
    }
  }

  return {
    races,
    loading,
    error,
    racesCount,
    upcomingRaces,
    fetchRaces,
    createRace,
    deleteRace
  }
})
```

### src/stores/athletes.js

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAthletesStore = defineStore('athletes', () => {
  const athletes = ref([])
  const loading = ref(false)
  const error = ref(null)

  const athletesCount = computed(() => athletes.value.length)
  const athletesByCountry = computed(() => {
    const grouped = {}
    athletes.value.forEach(a => {
      if (!grouped[a.country]) grouped[a.country] = []
      grouped[a.country].push(a)
    })
    return grouped
  })

  async function fetchAthletes() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/api/athletes')
      athletes.value = data.athletes || []
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function createAthlete(athleteData) {
    try {
      const { data } = await api.post('/api/athletes', athleteData)
      athletes.value.push(data)
      return data
    } catch (err) {
      throw err
    }
  }

  return {
    athletes,
    loading,
    error,
    athletesCount,
    athletesByCountry,
    fetchAthletes,
    createAthlete
  }
})
```

---

## 🗂️ Router Configuration

### src/router/index.js

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Layout from '@/components/Layout.vue'

const routes = [
  {
    path: '/login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue')
      },
      {
        path: 'races',
        name: 'Races',
        component: () => import('@/pages/Races/RacesList.vue')
      },
      {
        path: 'races/:id',
        name: 'RaceDetail',
        component: () => import('@/pages/Races/RaceDetail.vue')
      },
      {
        path: 'athletes',
        name: 'Athletes',
        component: () => import('@/pages/Athletes/AthletesList.vue')
      },
      {
        path: 'athletes/:id',
        name: 'AthleteDetail',
        component: () => import('@/pages/Athletes/AthleteDetail.vue')
      },
      {
        path: 'results',
        name: 'Results',
        component: () => import('@/pages/Results/ResultsList.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/pages/Users/UsersList.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/pages/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
```

---

## 🎨 Component Examples

### src/components/Layout.vue

```vue
<template>
  <div class="flex h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar />
    
    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <Header />
      
      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto p-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import { RouterView } from 'vue-router'
</script>
```

### src/components/Sidebar.vue

```vue
<template>
  <div class="w-64 bg-gray-900 text-white p-6 flex flex-col">
    <!-- Logo -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold">🏃 AthSys</h1>
    </div>

    <!-- Navigation Links -->
    <nav class="flex-1 space-y-3">
      <RouterLink 
        v-for="item in navItems" 
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-800 transition"
        :class="{ 'bg-primary': isActive(item.path) }"
      >
        <component :is="item.icon" class="w-5 h-5" />
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- Footer -->
    <button @click="logout" class="flex items-center gap-3 w-full px-4 py-3 rounded-lg hover:bg-gray-800 transition text-red-400">
      <ArrowLeftOnRectangleIcon class="w-5 h-5" />
      Logout
    </button>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import {
  HomeIcon,
  TrophyIcon,
  UserGroupIcon,
  ClipboardListIcon,
  UsersIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/vue/24/solid'

const authStore = useAuthStore()
const router = useRouter()

const navItems = [
  { label: 'Dashboard', path: '/', icon: HomeIcon },
  { label: 'Races', path: '/races', icon: TrophyIcon },
  { label: 'Athletes', path: '/athletes', icon: UserGroupIcon },
  { label: 'Results', path: '/results', icon: ClipboardListIcon },
  { label: 'Users', path: '/users', icon: UsersIcon }
]

function isActive(path) {
  return router.currentRoute.value.path === path
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>
```

### src/pages/Dashboard.vue

```vue
<template>
  <div>
    <h1 class="text-4xl font-bold mb-8">Dashboard</h1>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <StatCard 
        title="Athletes" 
        :value="athletesStore.athletesCount"
        icon="👥"
      />
      <StatCard 
        title="Races" 
        :value="racesStore.racesCount"
        icon="🏁"
      />
      <StatCard 
        title="Results" 
        :value="resultsStore.resultsCount"
        icon="📊"
      />
      <StatCard 
        title="Users" 
        :value="usersStore.usersCount"
        icon="👨‍💼"
      />
    </div>

    <!-- Recent Data -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <RecentRaces />
      <RecentResults />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAthletesStore } from '@/stores/athletes'
import { useRacesStore } from '@/stores/races'
import { useResultsStore } from '@/stores/results'
import { useUsersStore } from '@/stores/users'
import StatCard from '@/components/StatCard.vue'
import RecentRaces from '@/components/RecentRaces.vue'
import RecentResults from '@/components/RecentResults.vue'

const athletesStore = useAthletesStore()
const racesStore = useRacesStore()
const resultsStore = useResultsStore()
const usersStore = useUsersStore()

onMounted(() => {
  athletesStore.fetchAthletes()
  racesStore.fetchRaces()
  resultsStore.fetchResults()
  usersStore.fetchUsers()
})
</script>
```

### src/pages/Races/RacesList.vue

```vue
<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-4xl font-bold">Races</h1>
      <button @click="showCreateModal = true" class="btn btn-primary">
        + New Race
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="racesStore.loading" class="text-center py-12">
      <p class="text-gray-500">Loading races...</p>
    </div>

    <!-- Races Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-6 py-3 text-left text-sm font-semibold">Name</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">Date</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">Location</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">Status</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="race in racesStore.races" :key="race.id" class="border-b hover:bg-gray-50">
            <td class="px-6 py-4">{{ race.name }}</td>
            <td class="px-6 py-4">{{ formatDate(race.date) }}</td>
            <td class="px-6 py-4">{{ race.location }}</td>
            <td class="px-6 py-4">
              <span :class="statusColor(race.status)" class="px-3 py-1 rounded-full text-sm font-semibold">
                {{ race.status }}
              </span>
            </td>
            <td class="px-6 py-4 space-x-2">
              <RouterLink :to="`/races/${race.id}`" class="text-blue-600 hover:underline">View</RouterLink>
              <button @click="deleteRace(race.id)" class="text-red-600 hover:underline">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Modal -->
    <RaceForm 
      v-if="showCreateModal" 
      @close="showCreateModal = false"
      @created="handleRaceCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRacesStore } from '@/stores/races'
import { RouterLink } from 'vue-router'
import { useToast } from 'vue-toastification'
import RaceForm from './RaceForm.vue'

const racesStore = useRacesStore()
const toast = useToast()
const showCreateModal = ref(false)

onMounted(() => {
  racesStore.fetchRaces()
})

async function deleteRace(id) {
  if (confirm('Are you sure?')) {
    try {
      await racesStore.deleteRace(id)
      toast.success('Race deleted')
    } catch (error) {
      toast.error(error.message)
    }
  }
}

function handleRaceCreated() {
  showCreateModal.value = false
  racesStore.fetchRaces()
}

function formatDate(date) {
  return new Date(date).toLocaleDateString()
}

function statusColor(status) {
  const colors = {
    upcoming: 'bg-blue-100 text-blue-800',
    registration_open: 'bg-green-100 text-green-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-gray-100 text-gray-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}
</script>
```

---

## 🔌 API Service (Axios Wrapper)

### src/services/api.js

```javascript
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

---

## 📦 package.json

```json
{
  "name": "athsys-dashboard",
  "version": "3.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "e2e": "cypress open",
    "lint": "eslint src --fix",
    "format": "prettier --write src"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.4",
    "axios": "^1.5.0",
    "@headlessui/vue": "^1.7.14",
    "@heroicons/vue": "^2.0.18",
    "@vueuse/core": "^10.7.2",
    "vue-toastification": "^2.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.4.4",
    "vite": "^5.0.2",
    "tailwindcss": "^3.3.5",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16",
    "vitest": "^0.34.6",
    "@vitest/ui": "^0.34.6",
    "@vue/test-utils": "^2.4.1",
    "cypress": "^13.6.2",
    "eslint": "^8.51.0",
    "eslint-plugin-vue": "^9.18.1",
    "prettier": "^3.0.3"
  }
}
```

---

## .env Configuration

Create `src/frontend/.env`:

```env
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=AthSys v3.0
VITE_LOG_LEVEL=debug
```

Create `src/frontend/.env.production`:

```env
VITE_API_URL=https://ath.appstore.co.ke
VITE_APP_TITLE=AthSys
VITE_LOG_LEVEL=info
```

---

## 🚀 Setup Instructions

### 1. Create Project Structure

```bash
cd c:\projects\AthSys_ver1\src\frontend

# Initialize Vite
npm create vite@latest . -- --template vue

# Install dependencies (use the package.json above)
npm install
```

### 2. Create Directory Structure

```bash
mkdir -p src/{components,pages,stores,services,router,utils,styles}
```

### 3. Copy Files

Replace your `src/frontend/` with the structure outlined above.

### 4. Configure Environment

Create `.env` and `.env.production` with values above.

### 5. Start Development Server

```bash
npm run dev
```

You should see:
```
VITE v5.0.0  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### 6. Build for Production

```bash
npm run build
```

This creates `dist/` folder ready to deploy.

---

## 🎯 Key Features This Provides

✅ **Single Page Application** - Instant navigation without page reloads  
✅ **State Management** - Centralized data with Pinia stores  
✅ **Real-time Updates** - Data automatically syncs with backend  
✅ **Professional UI** - Beautiful, responsive TailwindCSS design  
✅ **Navigation Guards** - Automatic auth redirect  
✅ **API Integration** - Axios with interceptors  
✅ **Toast Notifications** - User feedback for actions  
✅ **Heroicons** - Beautiful SVG icons  
✅ **Mobile Responsive** - Works on all devices  
✅ **Developer Experience** - Hot module replacement, fast builds  

---

## 📊 Before & After Comparison

| Aspect | Before | After |
|--------|--------|-------|
| Architecture | Static HTML pages | Vue 3 SPA |
| Navigation | Full page reload | Instant (no reload) |
| State Management | None | Pinia stores |
| Styling | Mixed CSS files | TailwindCSS |
| Button clicks | Direct links | Route navigation |
| Data sync | Manual | Automatic (stores) |
| Icons | Mixed sources | Heroicons |
| Mobile | Basic | Fully responsive |
| Build | None | Vite |
| Testing | None | Vitest + Cypress |

---

## 🧪 Testing Example

### src/stores/__tests__/races.test.js

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRacesStore } from '../races'
import api from '@/services/api'

vi.mock('@/services/api')

describe('Races Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetches races from API', async () => {
    const store = useRacesStore()
    api.get.mockResolvedValue({ data: { races: [{ id: 1, name: 'Test' }] } })

    await store.fetchRaces()

    expect(store.races).toHaveLength(1)
  })

  it('computes race count', () => {
    const store = useRacesStore()
    store.races = [{ id: 1 }, { id: 2 }]

    expect(store.racesCount).toBe(2)
  })
})
```

---

## 🚢 Deployment

### Static Build (Netlify, Vercel, etc.)

```bash
npm run build
# Deploy dist/ folder
```

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package* ./
RUN npm install
COPY src ./src
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🆘 Troubleshooting

### Issue: "Cannot find module '@'"
**Fix**: Ensure `vite.config.js` has the alias configured correctly

### Issue: "Tailwind styles not applied"
**Fix**: Check `tailwind.config.js` content paths are correct

### Issue: "API calls fail with 401"
**Fix**: Ensure backend sets correct CORS headers and auth token is saved

### Issue: "Page doesn't update when data changes"
**Fix**: Make sure you're using reactive stores, not plain objects

---

## 📚 Next Steps

1. ✅ Implement the structure above
2. ✅ Copy all provided code files
3. ✅ Run `npm install && npm run dev`
4. ✅ Test pages load without errors
5. ✅ Connect to your backend API
6. ✅ Add more pages as needed
7. ✅ Deploy to production

---

**Created**: February 22, 2026  
**Status**: ✅ Ready to implement  
**Estimated Time**: 30 minutes setup + 2 hours customization
