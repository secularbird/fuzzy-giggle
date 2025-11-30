<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api/client';

const isHealthy = ref<boolean | null>(null);
const loading = ref(true);

async function checkHealth() {
  loading.value = true;
  try {
    const response = await api.healthCheck();
    isHealthy.value = response.status === 'healthy';
  } catch {
    isHealthy.value = false;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  checkHealth();
});
</script>

<template>
  <div>
    <!-- Hero section -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-8 mb-8 text-white">
      <h1 class="text-4xl font-bold mb-4">欢迎使用 Knowledge Server</h1>
      <p class="text-xl text-blue-100 mb-6">
        基于 RAG 技术的智能知识管理系统，支持向量搜索、知识图谱和网页抓取
      </p>
      
      <!-- Server status -->
      <div class="inline-flex items-center px-4 py-2 bg-white/10 rounded-full">
        <span 
          :class="[
            'w-3 h-3 rounded-full mr-2',
            loading ? 'bg-yellow-400 animate-pulse' : (isHealthy ? 'bg-green-400' : 'bg-red-400')
          ]"
        ></span>
        <span class="text-sm">
          {{ loading ? '检查服务器状态...' : (isHealthy ? '服务器运行正常' : '服务器离线') }}
        </span>
        <button 
          @click="checkHealth" 
          class="ml-2 text-blue-200 hover:text-white"
          :disabled="loading"
        >
          🔄
        </button>
      </div>
    </div>
    
    <!-- Quick actions -->
    <h2 class="text-2xl font-bold text-gray-900 mb-6">快速开始</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <router-link 
        to="/search" 
        class="block p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all"
      >
        <div class="text-4xl mb-4">🔍</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">搜索知识库</h3>
        <p class="text-gray-600">使用向量搜索和知识图谱查找相关文档和实体</p>
      </router-link>
      
      <router-link 
        to="/scrape" 
        class="block p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all"
      >
        <div class="text-4xl mb-4">🌐</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">网页抓取</h3>
        <p class="text-gray-600">从网页中提取内容并添加到知识库</p>
      </router-link>
      
      <router-link 
        to="/admin" 
        class="block p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all"
      >
        <div class="text-4xl mb-4">⚙️</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">管理后台</h3>
        <p class="text-gray-600">管理文档、实体和系统配置</p>
      </router-link>
    </div>
    
    <!-- Features -->
    <h2 class="text-2xl font-bold text-gray-900 mb-6">系统功能</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <span class="text-2xl mr-3">📊</span>
          向量数据库 (usearch)
        </h3>
        <p class="text-gray-600">
          高性能的向量相似度搜索，支持文档嵌入和语义搜索
        </p>
      </div>
      
      <div class="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <span class="text-2xl mr-3">🔗</span>
          知识图谱 (Kùzu DB)
        </h3>
        <p class="text-gray-600">
          存储文档、实体及其关系，支持图谱查询和关联分析
        </p>
      </div>
      
      <div class="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <span class="text-2xl mr-3">🤖</span>
          RAG 引擎
        </h3>
        <p class="text-gray-600">
          结合向量和图谱检索，为生成式 AI 提供增强的上下文
        </p>
      </div>
      
      <div class="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <span class="text-2xl mr-3">🕷️</span>
          网页爬虫 (Scrapy)
        </h3>
        <p class="text-gray-600">
          自动化网页内容提取，快速构建知识库
        </p>
      </div>
    </div>
  </div>
</template>
