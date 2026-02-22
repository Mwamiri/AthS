<template>
  <div class="flex h-screen bg-gray-50">
    <!-- Sidebar Navigation -->
    <Sidebar v-if="authStore.isAuthenticated" />
    
    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <Header v-if="authStore.isAuthenticated" />
      
      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import Header from '@/components/Header.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth from localStorage
  authStore.setAuthHeader()
})
</script>

<style scoped>
/* Root component styles */
</style>
