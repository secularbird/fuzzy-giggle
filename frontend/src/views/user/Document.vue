<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api, { type Document } from '../../api/client';

const route = useRoute();
const router = useRouter();

const document = ref<Document | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

async function loadDocument() {
  const docId = route.params.id as string;
  if (!docId) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    document.value = await api.getDocument(docId);
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载文档失败';
  } finally {
    loading.value = false;
  }
}

function goBack() {
  router.back();
}

onMounted(() => {
  loadDocument();
});
</script>

<template>
  <div>
    <!-- Back button -->
    <button
      @click="goBack"
      class="flex items-center text-gray-600 hover:text-gray-900 mb-6 transition-colors"
    >
      <span class="mr-2">⬅️</span>
      返回
    </button>
    
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
      <h2 class="text-lg font-semibold text-red-700 mb-2">加载失败</h2>
      <p class="text-red-600">{{ error }}</p>
      <button
        @click="loadDocument"
        class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        重试
      </button>
    </div>
    
    <!-- Document content -->
    <div v-else-if="document" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="p-6 border-b border-gray-200">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          {{ document.title }}
        </h1>
        <div class="flex flex-wrap gap-4 text-sm text-gray-500">
          <span class="flex items-center">
            <span class="mr-1">📄</span>
            ID: {{ document.doc_id }}
          </span>
          <a
            v-if="document.url"
            :href="document.url"
            target="_blank"
            class="flex items-center text-blue-600 hover:text-blue-700"
          >
            <span class="mr-1">🔗</span>
            {{ document.url }}
          </a>
        </div>
      </div>
      
      <div class="p-6">
        <div class="prose max-w-none">
          <p class="whitespace-pre-wrap text-gray-700 leading-relaxed">
            {{ document.content }}
          </p>
        </div>
      </div>
      
      <!-- Entities -->
      <div v-if="document.entities && document.entities.length > 0" class="p-6 bg-gray-50 border-t border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">相关实体</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="entity in document.entities"
            :key="entity.entity_id"
            class="p-4 bg-white rounded-lg border border-gray-200"
          >
            <h3 class="font-medium text-gray-900">{{ entity.name }}</h3>
            <p class="text-sm text-gray-500">{{ entity.entity_type }}</p>
            <p v-if="entity.description" class="mt-2 text-sm text-gray-600">
              {{ entity.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty state -->
    <div v-else class="bg-gray-50 rounded-xl p-8 text-center">
      <p class="text-gray-500">文档不存在</p>
    </div>
  </div>
</template>
