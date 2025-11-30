<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const currentPath = computed(() => route.path);

const navItems = [
  { path: '/admin', label: '概览', icon: '📊' },
  { path: '/admin/documents', label: '文档管理', icon: '📄' },
  { path: '/admin/entities', label: '实体管理', icon: '🔗' },
  { path: '/admin/settings', label: '系统设置', icon: '⚙️' },
];
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-gray-100 flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div class="p-4 border-b border-gray-700">
        <router-link to="/admin" class="flex items-center">
          <span class="text-2xl mr-2">🛠️</span>
          <span class="text-lg font-bold text-white">管理后台</span>
        </router-link>
      </div>
      
      <!-- Navigation -->
      <nav class="flex-1 p-4">
        <ul class="space-y-2">
          <li v-for="item in navItems" :key="item.path">
            <router-link
              :to="item.path"
              :class="[
                'flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                currentPath === item.path
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              ]"
            >
              <span class="mr-3 text-lg">{{ item.icon }}</span>
              {{ item.label }}
            </router-link>
          </li>
        </ul>
      </nav>
      
      <!-- Back to user -->
      <div class="p-4 border-t border-gray-700">
        <router-link
          to="/"
          class="flex items-center px-4 py-3 rounded-lg text-sm font-medium text-gray-400 hover:bg-gray-700 hover:text-white transition-colors"
        >
          <span class="mr-3">⬅️</span>
          返回用户界面
        </router-link>
      </div>
    </aside>
    
    <!-- Main content -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <header class="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <h1 class="text-xl font-semibold text-white">
          {{ $route.meta.title || '管理后台' }}
        </h1>
      </header>
      
      <!-- Content -->
      <main class="flex-1 p-6 overflow-auto">
        <slot />
      </main>
    </div>
  </div>
</template>
