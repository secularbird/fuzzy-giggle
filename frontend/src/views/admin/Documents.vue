<script setup lang="ts">
import { ref } from 'vue';
import api, { type Document } from '../../api/client';

// Form data
const formData = ref({
  doc_id: '',
  title: '',
  content: '',
  url: '',
});

const loading = ref(false);
const message = ref<{ type: 'success' | 'error'; text: string } | null>(null);

// View document
const viewDocId = ref('');
const viewedDocument = ref<Document | null>(null);
const viewLoading = ref(false);

async function addDocument() {
  if (!formData.value.doc_id || !formData.value.title || !formData.value.content) {
    message.value = { type: 'error', text: '请填写所有必填字段' };
    return;
  }
  
  loading.value = true;
  message.value = null;
  
  try {
    await api.addDocument({
      doc_id: formData.value.doc_id,
      title: formData.value.title,
      content: formData.value.content,
      url: formData.value.url || undefined,
    });
    
    message.value = { type: 'success', text: `文档 "${formData.value.doc_id}" 添加成功！` };
    
    // Reset form
    formData.value = { doc_id: '', title: '', content: '', url: '' };
  } catch (e) {
    message.value = { 
      type: 'error', 
      text: e instanceof Error ? e.message : '添加文档失败' 
    };
  } finally {
    loading.value = false;
  }
}

async function viewDocument() {
  if (!viewDocId.value) {
    message.value = { type: 'error', text: '请输入文档 ID' };
    return;
  }
  
  viewLoading.value = true;
  viewedDocument.value = null;
  message.value = null;
  
  try {
    const doc = await api.getDocument(viewDocId.value);
    viewedDocument.value = doc;
  } catch (e) {
    message.value = { 
      type: 'error', 
      text: e instanceof Error ? e.message : '获取文档失败' 
    };
  } finally {
    viewLoading.value = false;
  }
}

function resetForm() {
  formData.value = { doc_id: '', title: '', content: '', url: '' };
  message.value = null;
}
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Add document form -->
    <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-lg font-semibold text-white">添加文档</h2>
      </div>
      
      <form @submit.prevent="addDocument" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            文档 ID <span class="text-red-400">*</span>
          </label>
          <input
            v-model="formData.doc_id"
            type="text"
            placeholder="例如: doc_001"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            标题 <span class="text-red-400">*</span>
          </label>
          <input
            v-model="formData.title"
            type="text"
            placeholder="文档标题"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            内容 <span class="text-red-400">*</span>
          </label>
          <textarea
            v-model="formData.content"
            rows="6"
            placeholder="文档内容..."
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
          ></textarea>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            URL (可选)
          </label>
          <input
            v-model="formData.url"
            type="url"
            placeholder="https://example.com"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
        </div>
        
        <div class="flex gap-3 pt-2">
          <button
            type="button"
            @click="resetForm"
            class="px-4 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
          >
            重置
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? '添加中...' : '添加文档' }}
          </button>
        </div>
      </form>
    </div>
    
    <!-- View document -->
    <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-lg font-semibold text-white">查看文档</h2>
      </div>
      
      <div class="p-6">
        <div class="flex gap-3 mb-6">
          <input
            v-model="viewDocId"
            type="text"
            placeholder="输入文档 ID"
            class="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            @keyup.enter="viewDocument"
          />
          <button
            @click="viewDocument"
            :disabled="viewLoading || !viewDocId"
            class="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {{ viewLoading ? '加载中...' : '查看' }}
          </button>
        </div>
        
        <!-- Viewed document -->
        <div v-if="viewedDocument" class="bg-gray-700 rounded-lg p-4">
          <h3 class="text-lg font-semibold text-white mb-2">
            {{ viewedDocument.title }}
          </h3>
          <p class="text-gray-400 text-sm mb-4">
            ID: {{ viewedDocument.doc_id }}
            <span v-if="viewedDocument.url" class="ml-4">
              URL: <a :href="viewedDocument.url" target="_blank" class="text-blue-400 hover:underline">{{ viewedDocument.url }}</a>
            </span>
          </p>
          <p class="text-gray-300 whitespace-pre-wrap">
            {{ viewedDocument.content }}
          </p>
        </div>
        
        <div v-else class="text-center py-8 text-gray-500">
          输入文档 ID 查看文档内容
        </div>
      </div>
    </div>
    
    <!-- Message -->
    <div v-if="message" class="lg:col-span-2">
      <div
        :class="[
          'rounded-xl p-4',
          message.type === 'success' ? 'bg-green-900/50 border border-green-700 text-green-300' : 'bg-red-900/50 border border-red-700 text-red-300'
        ]"
      >
        {{ message.text }}
      </div>
    </div>
  </div>
</template>
