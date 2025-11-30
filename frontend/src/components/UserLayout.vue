<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const currentPath = computed(() => route.path);

const navItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/search', label: '搜索', icon: '🔍' },
  { path: '/scrape', label: '网页抓取', icon: '🌐' },
];
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <span class="text-2xl mr-2">📚</span>
              <span class="text-xl font-bold text-gray-900">Knowledge Server</span>
            </router-link>
          </div>
          
          <!-- Navigation -->
          <nav class="flex items-center space-x-4">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              :class="[
                'px-3 py-2 rounded-md text-sm font-medium transition-colors',
                currentPath === item.path
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              ]"
            >
              <span class="mr-1">{{ item.icon }}</span>
              {{ item.label }}
            </router-link>
            
            <!-- Admin link -->
            <router-link
              to="/admin"
              class="ml-4 px-4 py-2 bg-gray-800 text-white rounded-md text-sm font-medium hover:bg-gray-700 transition-colors"
            >
              ⚙️ 管理后台
            </router-link>
          </nav>
        </div>
      </div>
    </header>
    
    <!-- Main content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </main>
    
    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <p class="text-center text-gray-500 text-sm">
          © 2024 Knowledge Server. RAG-based knowledge management system.
        </p>
      </div>
    </footer>
  </div>
</template>
