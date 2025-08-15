<template>
  <div 
    class="question-group-builder bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-4 hover:border-blue-300 transition-colors"
    :class="{ 'dragging': isDragging, 'drag-over': isDragOver }"
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @dragover.prevent="handleDragOver"
    @dragleave="handleDragLeave"
    @drop.prevent="handleDrop"
  >
    <!-- Group Header -->
    <div class="group-header flex items-start justify-between mb-4">
      <div class="flex items-start space-x-3 flex-1">
        <!-- Drag Handle -->
        <div class="group-drag-handle cursor-move p-1 text-blue-400 hover:text-blue-600 mt-1">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
          </svg>
        </div>
        
        <!-- Group Type Badge -->
        <div class="group-type-badge bg-blue-600 text-white px-3 py-1 rounded-md text-xs font-medium mt-1 flex items-center space-x-1">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span>{{ displayTypeName }} Group</span>
        </div>
        
        <!-- Group Content -->
        <div class="flex-1 min-w-0">
          <div class="space-y-2">
            <!-- Group Name -->
            <div>
              <input
                v-model="editableGroup.name"
                @blur="updateGroup"
                @keyup.enter="updateGroup"
                placeholder="Group name"
                class="w-full text-lg font-semibold text-blue-900 bg-transparent border-none p-0 focus:ring-2 focus:ring-blue-500 rounded"
              />
            </div>
            
            <!-- Group Description -->
            <div class="text-sm text-blue-700">
              {{ group.questions.length }} question{{ group.questions.length !== 1 ? 's' : '' }} • {{ displayTypeName }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Group Actions -->
      <div class="flex items-center space-x-2 ml-4">
        <button
          @click="toggleSettings"
          class="p-1 text-blue-400 hover:text-blue-600 rounded-lg hover:bg-blue-100"
          title="Group settings"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </button>
        
        <button
          @click="duplicateGroup"
          class="p-1 text-blue-400 hover:text-blue-600 rounded-lg hover:bg-blue-100"
          title="Duplicate group"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
        </button>
        
        <button
          @click="deleteGroup"
          class="p-1 text-red-400 hover:text-red-600 rounded-lg hover:bg-red-50"
          title="Delete group"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Group Settings (collapsible) -->
    <div v-if="showSettings" class="group-settings mb-4 p-4 bg-white rounded-lg border border-blue-200">
      <h4 class="text-sm font-medium text-gray-900 mb-3">Group Settings</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Group Slug</label>
          <input
            v-model="editableGroup.slug"
            @blur="updateGroup"
            class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Display Type</label>
          <select
            v-model="editableGroup.display_type"
            @change="updateGroup"
            class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select type...</option>
            <option value="address">Address Block</option>
            <option value="contact">Contact Information</option>
            <option value="name">Name Fields</option>
            <option value="date_time">Date and Time</option>
            <option value="custom">Custom Group</option>
          </select>
        </div>
      </div>
      
      <div class="mt-3">
        <label class="block text-xs font-medium text-gray-700 mb-1">Configuration (JSON)</label>
        <textarea
          v-model="configJson"
          @blur="updateConfig"
          rows="3"
          class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          placeholder='{"layout": "stacked"}'
        />
      </div>
    </div>

    <!-- Questions in Group -->
    <div 
      @drop="handleQuestionDrop"
      @dragover.prevent
      @dragenter="handleQuestionDragEnter"
      @dragleave="handleQuestionDragLeave"
      class="group-questions-container min-h-20 p-3 bg-white rounded-lg border-2 border-dashed border-blue-200"
      :class="{ 'drag-over-question': isQuestionDragOver }"
    >
      <!-- Questions List -->
      <div v-if="group.questions && group.questions.length > 0" class="space-y-3">
        <QuestionBuilder
          v-for="(question, index) in group.questions"
          :key="question.id"
          :question="question"
          :question-types="questionTypes"
          :page-id="pageId"
          :form-slug="formSlug"
          :is-grouped="true"
          :group-id="group.id"
          @question-updated="handleQuestionUpdate"
          @question-deleted="handleQuestionDelete"
          @question-added="handleQuestionAdd"
          @question-reorder="handleQuestionReorder"
        />
      </div>
      
      <!-- Empty state for group -->
      <div v-else class="text-center py-6">
        <svg class="mx-auto h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
        </svg>
        <h4 class="mt-2 text-sm font-medium text-blue-700">No questions in group</h4>
        <p class="mt-1 text-xs text-blue-500">Drag question types here to add them to this group</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { formBuilderApi } from '../services/api.js'
import QuestionBuilder from './QuestionBuilder.vue'

// Props
const props = defineProps({
  group: {
    type: Object,
    required: true
  },
  formSlug: {
    type: String,
    required: true
  },
  pageId: {
    type: String,
    required: true
  },
  questionTypes: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits([
  'group-updated',
  'group-deleted',
  'question-added',
  'question-updated',
  'question-deleted',
  'question-reorder',
  'group-reorder'
])

// Reactive data
const editableGroup = ref({ ...props.group })
const showSettings = ref(false)
const isDragging = ref(false)
const isDragOver = ref(false)
const isQuestionDragOver = ref(false)

// Computed
const displayTypeName = computed(() => {
  const typeMap = {
    address: 'Address',
    contact: 'Contact',
    name: 'Name',
    date_time: 'Date/Time',
    custom: 'Custom',
    '': 'Generic'
  }
  return typeMap[editableGroup.value.display_type] || 'Generic'
})

const configJson = ref(JSON.stringify(props.group.config || {}, null, 2))

// Watch for prop changes
watch(() => props.group, (newGroup) => {
  editableGroup.value = { ...newGroup }
  configJson.value = JSON.stringify(newGroup.config || {}, null, 2)
}, { deep: true })

// Methods
const updateGroup = async () => {
  try {
    const response = await formBuilderApi.updateQuestionGroup(
      props.formSlug, 
      props.pageId, 
      props.group.id, 
      editableGroup.value
    )
    emit('group-updated', response.data)
  } catch (error) {
    console.error('Error updating group:', error)
  }
}

const updateConfig = async () => {
  try {
    const config = JSON.parse(configJson.value)
    editableGroup.value.config = config
    await updateGroup()
  } catch (error) {
    console.error('Invalid JSON config:', error)
    // Reset to valid JSON
    configJson.value = JSON.stringify(editableGroup.value.config || {}, null, 2)
  }
}

const deleteGroup = async () => {
  if (confirm(`Are you sure you want to delete the "${editableGroup.value.name}" group and all its questions?`)) {
    try {
      await formBuilderApi.deleteQuestionGroup(props.formSlug, props.pageId, props.group.id)
      emit('group-deleted', props.group.id)
    } catch (error) {
      console.error('Error deleting group:', error)
    }
  }
}

const duplicateGroup = async () => {
  try {
    const duplicateData = {
      name: `${editableGroup.value.name} (Copy)`,
      display_type: editableGroup.value.display_type,
      config: { ...editableGroup.value.config }
    }
    
    const response = await formBuilderApi.createQuestionGroup(props.formSlug, props.pageId, duplicateData)
    
    // Duplicate all questions in the group
    for (const question of props.group.questions) {
      const questionData = {
        name: question.name,
        text: question.text,
        type_slug: question.type?.slug || question.type,
        required: question.required,
        config: { ...question.config },
        validation: { ...question.validation },
        conditional_logic: { ...question.conditional_logic }
      }
      
      await formBuilderApi.addQuestionToGroup(props.formSlug, props.pageId, response.data.id, questionData)
    }
    
    emit('group-updated', response.data)
  } catch (error) {
    console.error('Error duplicating group:', error)
  }
}

// Event handlers for QuestionBuilder
const handleQuestionUpdate = (questionData) => {
  emit('question-updated', questionData)
}

const handleQuestionDelete = () => {
  // QuestionBuilder handles the deletion, we just need to emit the event
  emit('question-deleted')
}

const handleQuestionAdd = (questionData) => {
  emit('question-added', questionData)
}

const handleQuestionReorder = (reorderData) => {
  // Forward the reorder event to parent
  emit('question-reorder', reorderData)
}

// Drag and drop handlers
const handleDragStart = (event) => {
  isDragging.value = true
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/group-id', props.group.id)
}

const handleDragEnd = () => {
  isDragging.value = false
}

const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const draggedGroupId = event.dataTransfer.getData('text/group-id')
  
  if (draggedGroupId && draggedGroupId !== props.group.id) {
    // Emit group reorder event to parent
    emit('group-reorder', {
      draggedGroupId: draggedGroupId,
      targetGroupId: props.group.id
    })
  }
}

const handleQuestionDrop = async (event) => {
  event.preventDefault()
  isQuestionDragOver.value = false
  
  const questionTypeData = event.dataTransfer.getData('text/question-type')
  
  if (questionTypeData) {
    try {
      const questionType = JSON.parse(questionTypeData)
      
      const questionData = {
        name: `New ${questionType.name}`,
        text: `Enter your ${questionType.name.toLowerCase()}`,
        type_slug: questionType.slug,
        required: false,
        config: {},
        validation: {},
        conditional_logic: {}
      }
      
      const response = await formBuilderApi.addQuestionToGroup(
        props.formSlug, 
        props.pageId, 
        props.group.id, 
        questionData
      )
      
      emit('question-added', response.data)
    } catch (error) {
      console.error('Error adding question to group:', error)
    }
  }
}

const handleQuestionDragEnter = () => {
  isQuestionDragOver.value = true
}

const handleQuestionDragLeave = () => {
  isQuestionDragOver.value = false
}

const toggleSettings = () => {
  showSettings.value = !showSettings.value
}
</script>

<style scoped>
.drag-over {
  @apply border-blue-400 bg-blue-100;
}

.drag-over-question {
  @apply border-green-400 bg-green-50;
}

.dragging {
  @apply opacity-50;
}

.group-questions-container.drag-over-question {
  @apply border-green-400 bg-green-50;
}
</style>