<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api/client';

const stats = ref({
  serverStatus: 'checking',
  rerankingEnabled: false,
  currentModel: null as Record<string, unknown> | null,
});
const loading = ref(true);

async function loadStats() {
  loading.value = true;
  
  try {
    // Check server health
    const healthResponse = await api.healthCheck();
    stats.value.serverStatus = healthResponse.status === 'healthy' ? 'healthy' : 'unhealthy';
    
    // Get reranker info
    try {
      const rerankerResponse = await api.listRerankers();
      stats.value.rerankingEnabled = rerankerResponse.reranking_enabled;
      stats.value.currentModel = rerankerResponse.current_model;
    } catch {
      // Reranker endpoint might not be available
    }
  } catch {
    stats.value.serverStatus = 'offline';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadStats();
});
</script>

<template>
  <div>
    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-400 text-sm font-medium">服务器状态</h3>
          <span
            :class="[
              'w-3 h-3 rounded-full',
              loading ? 'bg-yellow-400 animate-pulse' : (stats.serverStatus === 'healthy' ? 'bg-green-400' : 'bg-red-400')
            ]"
          ></span>
        </div>
        <p class="text-2xl font-bold text-white">
          {{ loading ? '检查中...' : (stats.serverStatus === 'healthy' ? '运行正常' : '离线') }}
        </p>
      </div>
      
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-400 text-sm font-medium">重排序状态</h3>
          <span class="text-2xl">🔄</span>
        </div>
        <p class="text-2xl font-bold text-white">
          {{ stats.rerankingEnabled ? '已启用' : '未启用' }}
        </p>
      </div>
      
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-400 text-sm font-medium">当前模型</h3>
          <span class="text-2xl">🤖</span>
        </div>
        <p class="text-lg font-bold text-white truncate">
          {{ stats.currentModel ? 'ms-marco-MiniLM' : '默认' }}
        </p>
      </div>
    </div>
    
    <!-- Quick actions -->
    <h2 class="text-xl font-semibold text-white mb-4">快速操作</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <router-link
        to="/admin/documents"
        class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition-colors"
      >
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-4">📄</span>
          <div>
            <h3 class="text-lg font-semibold text-white">文档管理</h3>
            <p class="text-gray-400 text-sm">添加、编辑和删除文档</p>
          </div>
        </div>
      </router-link>
      
      <router-link
        to="/admin/entities"
        class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition-colors"
      >
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-4">🔗</span>
          <div>
            <h3 class="text-lg font-semibold text-white">实体管理</h3>
            <p class="text-gray-400 text-sm">管理知识图谱中的实体</p>
          </div>
        </div>
      </router-link>
      
      <router-link
        to="/admin/settings"
        class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition-colors"
      >
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-4">⚙️</span>
          <div>
            <h3 class="text-lg font-semibold text-white">系统设置</h3>
            <p class="text-gray-400 text-sm">配置服务器和 API 设置</p>
          </div>
        </div>
      </router-link>
      
      <router-link
        to="/"
        class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition-colors"
      >
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-4">👤</span>
          <div>
            <h3 class="text-lg font-semibold text-white">用户界面</h3>
            <p class="text-gray-400 text-sm">返回用户搜索界面</p>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>
