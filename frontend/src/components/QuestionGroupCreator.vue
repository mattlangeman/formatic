<template>
  <div class="question-group-creator">
    <!-- Question Group Types Palette -->
    <div class="group-types-section mb-6">
      <h3 class="text-sm font-medium text-gray-700 mb-3">Question Groups</h3>
      <div class="space-y-2">
        <div 
          v-for="template in groupTemplates" 
          :key="template.slug"
          @dragstart="startGroupDrag($event, template)"
          @dragend="endGroupDrag"
          draggable="true"
          class="group-type-item p-3 bg-blue-50 border border-blue-200 rounded-lg cursor-move hover:border-blue-300 hover:bg-blue-100 transition-all"
        >
          <div class="flex items-center space-x-3">
            <div class="group-type-icon w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
            </div>
            <div>
              <h4 class="text-sm font-medium text-blue-900">{{ template.name }}</h4>
              <p class="text-xs text-blue-600">{{ template.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Group Button -->
    <div class="create-group-section">
      <button
        @click="showCreateModal = true"
        class="w-full p-3 border-2 border-dashed border-blue-300 rounded-lg text-blue-600 hover:border-blue-400 hover:bg-blue-50 transition-colors flex items-center justify-center space-x-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
        </svg>
        <span class="text-sm font-medium">Create Question Group</span>
      </button>
    </div>

    <!-- Create Group Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Create Question Group</h3>
        
        <form @submit.prevent="createGroup">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Group Name</label>
              <input
                v-model="newGroup.name"
                type="text"
                placeholder="e.g., Contact Information"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Template</label>
              <select
                v-model="newGroup.template_slug"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select template...</option>
                <option v-for="template in groupTemplates" :key="template.slug" :value="template.slug">
                  {{ template.name }} - {{ template.description }}
                </option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="newGroup.description"
                rows="2"
                placeholder="Optional description"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              ></textarea>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="cancelCreate"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!newGroup.name"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Group
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { formBuilderApi, questionGroupTemplatesApi } from '../services/api.js'

// Props
const props = defineProps({
  formSlug: {
    type: String,
    required: true
  },
  pageId: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['group-created'])

// Reactive data
const showCreateModal = ref(false)
const groupTemplates = ref([])
const newGroup = ref({
  name: '',
  template_slug: '',
  description: '',
  config: {}
})

// Load templates on component mount
import { onMounted } from 'vue'

onMounted(async () => {
  await loadTemplates()
})

const loadTemplates = async () => {
  try {
    const response = await questionGroupTemplatesApi.getTemplates()
    groupTemplates.value = response.data
  } catch (error) {
    console.error('Failed to load group templates:', error)
  }
}

// Methods
const createGroup = async () => {
  try {
    const groupData = {
      name: newGroup.value.name,
      template_slug: newGroup.value.template_slug,
      config: {
        description: newGroup.value.description
      }
    }
    
    const response = await formBuilderApi.createQuestionGroup(
      props.formSlug, 
      props.pageId, 
      groupData
    )
    
    emit('group-created', response.data)
    cancelCreate()
  } catch (error) {
    console.error('Error creating group:', error)
  }
}

const cancelCreate = () => {
  showCreateModal.value = false
  newGroup.value = {
    name: '',
    template_slug: '',
    description: '',
    config: {}
  }
}

// Drag and drop for group types
const startGroupDrag = (event, template) => {
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('text/group-type', JSON.stringify(template))
}

const endGroupDrag = () => {
  // Clean up if needed
}
</script>

<style scoped>
.group-type-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
</style>