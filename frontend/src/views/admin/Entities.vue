<script setup lang="ts">
import { ref } from 'vue';
import api, { type Entity } from '../../api/client';

// Form data for adding entity
const entityForm = ref({
  entity_id: '',
  name: '',
  entity_type: '',
  description: '',
});

// Form data for linking entities
const linkForm = ref({
  source_id: '',
  target_id: '',
  relation_type: '',
});

const loading = ref(false);
const linkLoading = ref(false);
const message = ref<{ type: 'success' | 'error'; text: string } | null>(null);

// View entity
const viewEntityId = ref('');
const viewedEntity = ref<Entity | null>(null);
const relatedEntities = ref<Entity[]>([]);
const viewLoading = ref(false);

async function addEntity() {
  if (!entityForm.value.entity_id || !entityForm.value.name || !entityForm.value.entity_type) {
    message.value = { type: 'error', text: '请填写所有必填字段' };
    return;
  }
  
  loading.value = true;
  message.value = null;
  
  try {
    await api.addEntity({
      entity_id: entityForm.value.entity_id,
      name: entityForm.value.name,
      entity_type: entityForm.value.entity_type,
      description: entityForm.value.description || undefined,
    });
    
    message.value = { type: 'success', text: `实体 "${entityForm.value.name}" 添加成功！` };
    
    // Reset form
    entityForm.value = { entity_id: '', name: '', entity_type: '', description: '' };
  } catch (e) {
    message.value = { 
      type: 'error', 
      text: e instanceof Error ? e.message : '添加实体失败' 
    };
  } finally {
    loading.value = false;
  }
}

async function linkEntities() {
  if (!linkForm.value.source_id || !linkForm.value.target_id || !linkForm.value.relation_type) {
    message.value = { type: 'error', text: '请填写所有必填字段' };
    return;
  }
  
  linkLoading.value = true;
  message.value = null;
  
  try {
    await api.linkEntities({
      source_id: linkForm.value.source_id,
      target_id: linkForm.value.target_id,
      relation_type: linkForm.value.relation_type,
    });
    
    message.value = { type: 'success', text: '实体关联成功！' };
    
    // Reset form
    linkForm.value = { source_id: '', target_id: '', relation_type: '' };
  } catch (e) {
    message.value = { 
      type: 'error', 
      text: e instanceof Error ? e.message : '关联实体失败' 
    };
  } finally {
    linkLoading.value = false;
  }
}

async function viewEntity() {
  if (!viewEntityId.value) {
    message.value = { type: 'error', text: '请输入实体 ID' };
    return;
  }
  
  viewLoading.value = true;
  viewedEntity.value = null;
  relatedEntities.value = [];
  message.value = null;
  
  try {
    const entity = await api.getEntity(viewEntityId.value);
    viewedEntity.value = entity;
    
    // Get related entities
    try {
      const related = await api.getRelatedEntities(viewEntityId.value);
      relatedEntities.value = related;
    } catch {
      // Related entities might not exist
    }
  } catch (e) {
    message.value = { 
      type: 'error', 
      text: e instanceof Error ? e.message : '获取实体失败' 
    };
  } finally {
    viewLoading.value = false;
  }
}

function resetEntityForm() {
  entityForm.value = { entity_id: '', name: '', entity_type: '', description: '' };
  message.value = null;
}

function resetLinkForm() {
  linkForm.value = { source_id: '', target_id: '', relation_type: '' };
  message.value = null;
}
</script>

<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Add entity form -->
      <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div class="p-4 border-b border-gray-700">
          <h2 class="text-lg font-semibold text-white">添加实体</h2>
        </div>
        
        <form @submit.prevent="addEntity" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              实体 ID <span class="text-red-400">*</span>
            </label>
            <input
              v-model="entityForm.entity_id"
              type="text"
              placeholder="例如: entity_001"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              名称 <span class="text-red-400">*</span>
            </label>
            <input
              v-model="entityForm.name"
              type="text"
              placeholder="实体名称"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              类型 <span class="text-red-400">*</span>
            </label>
            <select
              v-model="entityForm.entity_type"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            >
              <option value="">选择类型</option>
              <option value="person">人物 (Person)</option>
              <option value="organization">组织 (Organization)</option>
              <option value="location">地点 (Location)</option>
              <option value="concept">概念 (Concept)</option>
              <option value="technology">技术 (Technology)</option>
              <option value="event">事件 (Event)</option>
              <option value="product">产品 (Product)</option>
              <option value="other">其他 (Other)</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              描述 (可选)
            </label>
            <textarea
              v-model="entityForm.description"
              rows="3"
              placeholder="实体描述..."
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
            ></textarea>
          </div>
          
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="resetEntityForm"
              class="px-4 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
            >
              重置
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              {{ loading ? '添加中...' : '添加实体' }}
            </button>
          </div>
        </form>
      </div>
      
      <!-- Link entities form -->
      <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div class="p-4 border-b border-gray-700">
          <h2 class="text-lg font-semibold text-white">关联实体</h2>
        </div>
        
        <form @submit.prevent="linkEntities" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              源实体 ID <span class="text-red-400">*</span>
            </label>
            <input
              v-model="linkForm.source_id"
              type="text"
              placeholder="源实体 ID"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              关系类型 <span class="text-red-400">*</span>
            </label>
            <select
              v-model="linkForm.relation_type"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            >
              <option value="">选择关系类型</option>
              <option value="related_to">相关于 (Related To)</option>
              <option value="part_of">属于 (Part Of)</option>
              <option value="created_by">创建者 (Created By)</option>
              <option value="located_in">位于 (Located In)</option>
              <option value="works_for">工作于 (Works For)</option>
              <option value="belongs_to">归属于 (Belongs To)</option>
              <option value="associated_with">关联 (Associated With)</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              目标实体 ID <span class="text-red-400">*</span>
            </label>
            <input
              v-model="linkForm.target_id"
              type="text"
              placeholder="目标实体 ID"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>
          
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="resetLinkForm"
              class="px-4 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
            >
              重置
            </button>
            <button
              type="submit"
              :disabled="linkLoading"
              class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              {{ linkLoading ? '关联中...' : '创建关联' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- View entity -->
    <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-lg font-semibold text-white">查看实体</h2>
      </div>
      
      <div class="p-6">
        <div class="flex gap-3 mb-6">
          <input
            v-model="viewEntityId"
            type="text"
            placeholder="输入实体 ID"
            class="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            @keyup.enter="viewEntity"
          />
          <button
            @click="viewEntity"
            :disabled="viewLoading || !viewEntityId"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {{ viewLoading ? '加载中...' : '查看' }}
          </button>
        </div>
        
        <!-- Viewed entity -->
        <div v-if="viewedEntity" class="space-y-4">
          <div class="bg-gray-700 rounded-lg p-4">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="text-lg font-semibold text-white mb-1">
                  {{ viewedEntity.name }}
                </h3>
                <p class="text-gray-400 text-sm">
                  ID: {{ viewedEntity.entity_id }} | 类型: {{ viewedEntity.entity_type }}
                </p>
              </div>
              <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-sm">
                {{ viewedEntity.entity_type }}
              </span>
            </div>
            <p v-if="viewedEntity.description" class="text-gray-300 mt-3">
              {{ viewedEntity.description }}
            </p>
          </div>
          
          <!-- Related entities -->
          <div v-if="relatedEntities.length > 0">
            <h4 class="text-md font-medium text-gray-300 mb-3">相关实体</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div
                v-for="related in relatedEntities"
                :key="related.entity_id"
                class="bg-gray-700 rounded-lg p-3"
              >
                <p class="text-white font-medium">{{ related.name }}</p>
                <p class="text-gray-400 text-sm">{{ related.entity_type }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-8 text-gray-500">
          输入实体 ID 查看实体详情
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
