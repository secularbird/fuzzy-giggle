<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api, { type SearchResult } from '../../api/client';

const router = useRouter();

const query = ref('');
const results = ref<SearchResult[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const searched = ref(false);

// Search options
const topK = ref(5);
const includeGraph = ref(true);
const useReranker = ref(false);

async function search() {
  if (!query.value.trim()) return;
  
  loading.value = true;
  error.value = null;
  searched.value = true;
  
  try {
    const response = await api.search(
      query.value,
      topK.value,
      includeGraph.value,
      undefined,
      useReranker.value
    );
    results.value = response.results;
  } catch (e) {
    error.value = e instanceof Error ? e.message : '搜索失败';
    results.value = [];
  } finally {
    loading.value = false;
  }
}

function viewDocument(id: number) {
  router.push(`/document/${id}`);
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">搜索知识库</h1>
    
    <!-- Search form -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <form @submit.prevent="search" class="space-y-4">
        <div class="flex gap-4">
          <input
            v-model="query"
            type="text"
            placeholder="输入搜索关键词..."
            class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
          <button
            type="submit"
            :disabled="loading || !query.trim()"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? '搜索中...' : '🔍 搜索' }}
          </button>
        </div>
        
        <!-- Search options -->
        <div class="flex flex-wrap gap-6 pt-2">
          <label class="flex items-center gap-2 text-gray-600">
            <span>返回结果数:</span>
            <select
              v-model.number="topK"
              class="px-3 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            >
              <option :value="3">3</option>
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="20">20</option>
            </select>
          </label>
          
          <label class="flex items-center gap-2 text-gray-600 cursor-pointer">
            <input
              v-model="includeGraph"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span>包含图谱上下文</span>
          </label>
          
          <label class="flex items-center gap-2 text-gray-600 cursor-pointer">
            <input
              v-model="useReranker"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span>使用重排序</span>
          </label>
        </div>
      </form>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
      <p class="text-red-600">
        <span class="font-medium">错误:</span> {{ error }}
      </p>
    </div>
    
    <!-- Results -->
    <div v-if="searched && !loading" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-900">
          搜索结果
          <span class="text-gray-500 font-normal">({{ results.length }} 条)</span>
        </h2>
      </div>
      
      <div v-if="results.length === 0" class="bg-gray-50 rounded-xl p-8 text-center">
        <p class="text-gray-500">未找到相关结果</p>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="result in results"
          :key="result.id"
          class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
          @click="viewDocument(result.id)"
        >
          <div class="flex justify-between items-start mb-3">
            <h3 class="text-lg font-semibold text-gray-900">
              文档 #{{ result.id }}
            </h3>
            <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
              相似度: {{ (result.score * 100).toFixed(1) }}%
            </span>
          </div>
          
          <p v-if="result.content" class="text-gray-600 line-clamp-3">
            {{ result.content }}
          </p>
          
          <!-- Reranking info -->
          <div v-if="result.reranked" class="mt-3 text-sm text-gray-500">
            <span class="inline-flex items-center px-2 py-1 bg-green-100 text-green-700 rounded">
              ✓ 已重排序
            </span>
            <span v-if="result.original_score" class="ml-2">
              原始分数: {{ (result.original_score * 100).toFixed(1) }}%
            </span>
          </div>
          
          <!-- Entities -->
          <div v-if="result.entities && result.entities.length > 0" class="mt-4">
            <p class="text-sm text-gray-500 mb-2">相关实体:</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="entity in result.entities"
                :key="entity.entity_id"
                class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
              >
                {{ entity.name }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
