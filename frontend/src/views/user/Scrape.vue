<script setup lang="ts">
import { ref } from 'vue';
import api, { type ScrapeResult } from '../../api/client';

const urls = ref('');
const addToKnowledgeBase = ref(true);
const results = ref<ScrapeResult[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

async function scrape() {
  const urlList = urls.value
    .split('\n')
    .map(url => url.trim())
    .filter(url => url.length > 0);
  
  if (urlList.length === 0) {
    error.value = '请输入至少一个 URL';
    return;
  }
  
  // Validate URLs
  const invalidUrls = urlList.filter(url => {
    try {
      new URL(url);
      return false;
    } catch {
      return true;
    }
  });
  
  if (invalidUrls.length > 0) {
    error.value = `无效的 URL: ${invalidUrls.join(', ')}`;
    return;
  }
  
  loading.value = true;
  error.value = null;
  results.value = [];
  
  try {
    const response = await api.scrapeUrls({
      urls: urlList,
      add_to_knowledge_base: addToKnowledgeBase.value,
    });
    results.value = response.scraped;
  } catch (e) {
    error.value = e instanceof Error ? e.message : '抓取失败';
  } finally {
    loading.value = false;
  }
}

function clearResults() {
  results.value = [];
  error.value = null;
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">网页抓取</h1>
    
    <!-- Scrape form -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <form @submit.prevent="scrape" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            URLs (每行一个)
          </label>
          <textarea
            v-model="urls"
            rows="5"
            placeholder="https://example.com&#10;https://another-site.com"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
          ></textarea>
        </div>
        
        <div class="flex flex-wrap items-center gap-6">
          <label class="flex items-center gap-2 text-gray-600 cursor-pointer">
            <input
              v-model="addToKnowledgeBase"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span>添加到知识库</span>
          </label>
          
          <div class="flex gap-3 ml-auto">
            <button
              v-if="results.length > 0"
              type="button"
              @click="clearResults"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              清除结果
            </button>
            <button
              type="submit"
              :disabled="loading || !urls.trim()"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {{ loading ? '抓取中...' : '🕷️ 开始抓取' }}
            </button>
          </div>
        </div>
      </form>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
      <p class="text-red-600">
        <span class="font-medium">错误:</span> {{ error }}
      </p>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-4"></div>
      <p class="text-gray-500">正在抓取网页内容...</p>
    </div>
    
    <!-- Results -->
    <div v-if="results.length > 0 && !loading" class="space-y-4">
      <h2 class="text-xl font-semibold text-gray-900">
        抓取结果
        <span class="text-gray-500 font-normal">({{ results.length }} 条)</span>
      </h2>
      
      <div class="space-y-4">
        <div
          v-for="(result, index) in results"
          :key="index"
          :class="[
            'bg-white rounded-xl shadow-sm border p-6',
            result.error ? 'border-red-200' : 'border-gray-200'
          ]"
        >
          <div class="flex items-start justify-between mb-3">
            <a
              :href="result.url"
              target="_blank"
              class="text-blue-600 hover:text-blue-700 hover:underline font-medium"
            >
              {{ result.url }}
            </a>
            <span
              :class="[
                'px-3 py-1 rounded-full text-sm font-medium',
                result.error ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
              ]"
            >
              {{ result.error ? '失败' : '成功' }}
            </span>
          </div>
          
          <div v-if="result.error" class="text-red-600">
            <p class="font-medium">错误信息:</p>
            <p>{{ result.error }}</p>
          </div>
          
          <div v-else>
            <h3 v-if="result.title" class="text-lg font-semibold text-gray-900 mb-2">
              {{ result.title }}
            </h3>
            <p v-if="result.content" class="text-gray-600 line-clamp-5">
              {{ result.content }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-5 {
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
