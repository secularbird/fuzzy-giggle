<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api/client';

const serverUrl = ref('http://localhost:8000');
const saving = ref(false);
const testing = ref(false);
const message = ref<{ type: 'success' | 'error'; text: string } | null>(null);

// Reranker info
const rerankerInfo = ref<{
  available_models: Record<string, unknown>;
  current_model: Record<string, unknown> | null;
  reranking_enabled: boolean;
} | null>(null);

async function testConnection() {
  testing.value = true;
  message.value = null;
  
  try {
    api.setBaseURL(serverUrl.value);
    const response = await api.healthCheck();
    
    if (response.status === 'healthy') {
      message.value = { type: 'success', text: '连接成功！服务器运行正常。' };
      
      // Load reranker info
      try {
        rerankerInfo.value = await api.listRerankers();
      } catch {
        // Reranker endpoint might not be available
      }
    } else {
      message.value = { type: 'error', text: '服务器响应异常' };
    }
  } catch (e) {
    message.value = { 
      type: 'error', 
      text: `连接失败: ${e instanceof Error ? e.message : '未知错误'}` 
    };
  } finally {
    testing.value = false;
  }
}

function saveSettings() {
  saving.value = true;
  message.value = null;
  
  try {
    api.setBaseURL(serverUrl.value);
    localStorage.setItem('knowledge_server_url', serverUrl.value);
    message.value = { type: 'success', text: '设置已保存！' };
  } catch (e) {
    message.value = { 
      type: 'error', 
      text: `保存失败: ${e instanceof Error ? e.message : '未知错误'}` 
    };
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  // Load saved settings
  const savedUrl = localStorage.getItem('knowledge_server_url');
  if (savedUrl) {
    serverUrl.value = savedUrl;
    api.setBaseURL(savedUrl);
  }
  
  // Test connection on mount
  testConnection();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Server settings -->
    <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-lg font-semibold text-white">服务器设置</h2>
      </div>
      
      <div class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            服务器地址
          </label>
          <div class="flex gap-3">
            <input
              v-model="serverUrl"
              type="url"
              placeholder="http://localhost:8000"
              class="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <button
              @click="testConnection"
              :disabled="testing"
              class="px-4 py-2 bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              {{ testing ? '测试中...' : '测试连接' }}
            </button>
            <button
              @click="saveSettings"
              :disabled="saving"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
        
        <p class="text-gray-400 text-sm">
          设置 Knowledge Server 的 API 地址。默认为 http://localhost:8000
        </p>
      </div>
    </div>
    
    <!-- Reranker settings -->
    <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-lg font-semibold text-white">重排序设置</h2>
      </div>
      
      <div class="p-6">
        <div v-if="rerankerInfo" class="space-y-4">
          <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <h3 class="text-white font-medium">重排序状态</h3>
              <p class="text-gray-400 text-sm">当前重排序功能状态</p>
            </div>
            <span
              :class="[
                'px-4 py-2 rounded-lg font-medium',
                rerankerInfo.reranking_enabled ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
              ]"
            >
              {{ rerankerInfo.reranking_enabled ? '已启用' : '未启用' }}
            </span>
          </div>
          
          <div v-if="rerankerInfo.current_model" class="p-4 bg-gray-700 rounded-lg">
            <h3 class="text-white font-medium mb-2">当前模型</h3>
            <pre class="text-gray-300 text-sm overflow-x-auto">{{ JSON.stringify(rerankerInfo.current_model, null, 2) }}</pre>
          </div>
          
          <div v-if="rerankerInfo.available_models" class="p-4 bg-gray-700 rounded-lg">
            <h3 class="text-white font-medium mb-2">可用模型</h3>
            <pre class="text-gray-300 text-sm overflow-x-auto">{{ JSON.stringify(rerankerInfo.available_models, null, 2) }}</pre>
          </div>
        </div>
        
        <div v-else class="text-center py-8 text-gray-500">
          正在加载重排序信息...
        </div>
        
        <div class="mt-4 p-4 bg-gray-700/50 rounded-lg">
          <p class="text-gray-400 text-sm">
            <strong class="text-gray-300">提示:</strong> 
            重排序设置需要通过环境变量配置:
          </p>
          <ul class="mt-2 text-gray-400 text-sm list-disc list-inside">
            <li><code class="text-blue-400">KNOWLEDGE_USE_RERANKER=true</code> - 启用重排序</li>
            <li><code class="text-blue-400">KNOWLEDGE_RERANKER_MODEL=ms-marco-MiniLM-L-6-v2</code> - 设置模型</li>
          </ul>
        </div>
      </div>
    </div>
    
    <!-- API Endpoints -->
    <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-lg font-semibold text-white">API 端点参考</h2>
      </div>
      
      <div class="p-6">
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="text-gray-400 border-b border-gray-700">
                <th class="py-3 px-4">端点</th>
                <th class="py-3 px-4">方法</th>
                <th class="py-3 px-4">描述</th>
              </tr>
            </thead>
            <tbody class="text-gray-300">
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/health</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-green-600 text-white rounded text-xs">GET</span></td>
                <td class="py-3 px-4">健康检查</td>
              </tr>
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/documents</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-blue-600 text-white rounded text-xs">POST</span></td>
                <td class="py-3 px-4">添加文档</td>
              </tr>
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/documents/{'{doc_id}'}</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-green-600 text-white rounded text-xs">GET</span></td>
                <td class="py-3 px-4">获取文档</td>
              </tr>
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/entities</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-blue-600 text-white rounded text-xs">POST</span></td>
                <td class="py-3 px-4">添加实体</td>
              </tr>
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/entities/{'{entity_id}'}</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-green-600 text-white rounded text-xs">GET</span></td>
                <td class="py-3 px-4">获取实体</td>
              </tr>
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/entities/link</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-blue-600 text-white rounded text-xs">POST</span></td>
                <td class="py-3 px-4">关联实体</td>
              </tr>
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/search</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-blue-600 text-white rounded text-xs">POST</span></td>
                <td class="py-3 px-4">搜索知识库</td>
              </tr>
              <tr class="border-b border-gray-700">
                <td class="py-3 px-4 font-mono text-sm">/context</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-blue-600 text-white rounded text-xs">POST</span></td>
                <td class="py-3 px-4">获取上下文</td>
              </tr>
              <tr>
                <td class="py-3 px-4 font-mono text-sm">/scrape</td>
                <td class="py-3 px-4"><span class="px-2 py-1 bg-blue-600 text-white rounded text-xs">POST</span></td>
                <td class="py-3 px-4">网页抓取</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Message -->
    <div v-if="message">
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
