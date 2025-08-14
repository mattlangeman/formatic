<template>
  <div 
    class="question-builder bg-gray-50 border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
    :class="{ 'dragging': isDragging, 'drag-over': isDragOver }"
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @dragover.prevent="handleDragOver"
    @dragleave="handleDragLeave"
    @drop.prevent="handleDrop"
  >
    <div class="question-header flex items-start justify-between mb-4">
      <div class="flex items-start space-x-3 flex-1">
        <!-- Drag Handle -->
        <div class="question-drag-handle cursor-move p-1 text-gray-400 hover:text-gray-600 mt-1">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
          </svg>
        </div>
        
        <!-- Question Type Icon -->
        <div class="question-type-badge bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs font-medium mt-1">
          {{ questionTypeName }}
        </div>
        
        <!-- Question Content -->
        <div class="flex-1 min-w-0">
          <div class="space-y-2">
            <!-- Question Name (Primary) -->
            <div>
              <input
                v-model="editableQuestion.name"
                @blur="updateQuestion"
                @keyup.enter="updateQuestion"
                placeholder="Question name"
                class="w-full text-base font-medium text-gray-900 bg-transparent border-none p-0 focus:ring-2 focus:ring-blue-500 rounded"
              />
            </div>
            
            <!-- Question Text (Secondary) -->
            <div>
              <input
                v-model="editableQuestion.text"
                @blur="updateQuestion"
                @keyup.enter="updateQuestion"
                placeholder="Question text"
                class="w-full text-sm text-gray-600 bg-transparent border-none p-0 focus:ring-2 focus:ring-blue-500 rounded"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Question Actions -->
      <div class="flex items-center space-x-2 ml-4">
        <button
          @click="toggleRequired"
          :class="[
            'p-1 rounded-lg text-xs font-medium px-2 py-1',
            editableQuestion.required 
              ? 'bg-red-100 text-red-800' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
          title="Toggle required"
        >
          {{ editableQuestion.required ? 'Required' : 'Optional' }}
        </button>
        
        <button
          @click="toggleSettings"
          class="p-1 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          title="Question settings"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </button>
        
        <button
          @click="duplicateQuestion"
          class="p-1 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          title="Duplicate question"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
        </button>
        
        <button
          @click="deleteQuestion"
          class="p-1 text-red-400 hover:text-red-600 rounded-lg hover:bg-red-50"
          title="Delete question"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Question Settings Panel -->
    <div v-if="showSettings" class="question-settings mt-4 pt-4 border-t border-gray-200 bg-white rounded-lg p-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Basic Settings -->
        <div class="space-y-4">
          <h4 class="text-sm font-medium text-gray-900">Basic Settings</h4>
          
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Question Subtext</label>
            <input
              v-model="editableQuestion.subtext"
              @blur="updateQuestion"
              placeholder="Optional description or help text"
              class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Question Slug</label>
            <input
              v-model="editableQuestion.slug"
              @blur="updateQuestion"
              class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        <!-- Question Type Specific Configuration -->
        <div class="space-y-4">
          <h4 class="text-sm font-medium text-gray-900">Configuration</h4>
          
          <!-- Dynamic configuration based on question type -->
          <div v-if="questionType">
            <QuestionTypeConfiguration
              :question="editableQuestion"
              :question-type="questionType"
              @update-config="updateQuestionConfig"
            />
          </div>
        </div>
      </div>

      <!-- Validation Settings -->
      <div class="mt-6 pt-4 border-t border-gray-200">
        <h4 class="text-sm font-medium text-gray-900 mb-4">Validation</h4>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="flex items-center">
              <input
                v-model="editableQuestion.required"
                @change="updateQuestion"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">Required field</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Advanced Settings -->
      <div class="mt-6 pt-4 border-t border-gray-200">
        <button
          @click="showAdvanced = !showAdvanced"
          class="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          <svg 
            :class="['w-4 h-4 mr-2 transition-transform', showAdvanced ? 'rotate-90' : '']"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
          Advanced Settings
        </button>
        
        <div v-if="showAdvanced" class="mt-4 space-y-4">
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Conditional Logic (JSON)</label>
            <textarea
              v-model="conditionalLogicString"
              @blur="updateConditionalLogic"
              rows="3"
              class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
              placeholder='{"show_if": {"field": "other_field", "value": "yes"}}'
            ></textarea>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { formBuilderApi } from '../services/api.js'
import QuestionTypeConfiguration from './QuestionTypeConfiguration.vue'

// Props
const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  questionTypes: {
    type: Array,
    default: () => []
  },
  pageId: {
    type: String,
    required: true
  },
  formSlug: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['question-updated', 'question-deleted', 'question-reorder', 'question-added'])

// Reactive data
const editableQuestion = ref({ ...props.question })
const showSettings = ref(false)
const showAdvanced = ref(false)
const isDragging = ref(false)
const isDragOver = ref(false)

// Computed properties
const questionType = computed(() => {
  return props.questionTypes.find(qt => qt.slug === props.question.type?.slug)
})

const questionTypeName = computed(() => {
  return questionType.value?.name || props.question.type?.name || 'Unknown'
})

const conditionalLogicString = ref(JSON.stringify(props.question.conditional_logic || {}, null, 2))

// Watch for prop changes
watch(() => props.question, (newQuestion) => {
  editableQuestion.value = { ...newQuestion }
  conditionalLogicString.value = JSON.stringify(newQuestion.conditional_logic || {}, null, 2)
}, { deep: true })

// Update question
const updateQuestion = async () => {
  try {
    const updateData = {
      name: editableQuestion.value.name,
      slug: editableQuestion.value.slug,
      text: editableQuestion.value.text,
      subtext: editableQuestion.value.subtext,
      required: editableQuestion.value.required,
      config: editableQuestion.value.config || {},
      validation: editableQuestion.value.validation || {},
      conditional_logic: editableQuestion.value.conditional_logic || {}
    }
    
    const response = await formBuilderApi.updateQuestion(
      props.formSlug,
      props.pageId,
      props.question.id,
      updateData
    )
    
    emit('question-updated', response.data)
  } catch (error) {
    console.error('Failed to update question:', error)
  }
}

// Update question configuration
const updateQuestionConfig = (newConfig) => {
  editableQuestion.value.config = { ...editableQuestion.value.config, ...newConfig }
  updateQuestion()
}

// Toggle required status
const toggleRequired = () => {
  editableQuestion.value.required = !editableQuestion.value.required
  updateQuestion()
}

// Toggle settings panel
const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

// Update conditional logic from JSON string
const updateConditionalLogic = () => {
  try {
    editableQuestion.value.conditional_logic = JSON.parse(conditionalLogicString.value)
    updateQuestion()
  } catch (error) {
    console.error('Invalid JSON in conditional logic:', error)
    // Reset to original value
    conditionalLogicString.value = JSON.stringify(editableQuestion.value.conditional_logic || {}, null, 2)
  }
}

// Duplicate question
const duplicateQuestion = async () => {
  try {
    const duplicateData = {
      type_slug: questionType.value.slug,
      name: `${editableQuestion.value.name} (Copy)`,
      slug: `${editableQuestion.value.slug}-copy-${Date.now()}`,
      text: editableQuestion.value.text,
      subtext: editableQuestion.value.subtext,
      required: editableQuestion.value.required,
      config: { ...editableQuestion.value.config },
      validation: { ...editableQuestion.value.validation },
      conditional_logic: { ...editableQuestion.value.conditional_logic }
    }
    
    const response = await formBuilderApi.createQuestion(
      props.formSlug,
      props.pageId,
      duplicateData
    )
    
    // Emit the new question to update parent state
    emit('question-added', response.data)
  } catch (error) {
    console.error('Failed to duplicate question:', error)
  }
}

// Delete question
const deleteQuestion = async () => {
  if (confirm(`Are you sure you want to delete this question: "${editableQuestion.value.name}"?`)) {
    try {
      await formBuilderApi.deleteQuestion(
        props.formSlug,
        props.pageId,
        props.question.id
      )
      emit('question-deleted')
    } catch (error) {
      console.error('Failed to delete question:', error)
    }
  }
}

// Drag and drop handlers
const handleDragStart = (event) => {
  isDragging.value = true
  const questionData = {
    id: props.question.id,
    type: 'question',
    pageId: props.pageId,
    order: props.question.order
  }
  event.dataTransfer.setData('application/json', JSON.stringify(questionData))
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragEnd = () => {
  isDragging.value = false
}

const handleDragOver = (event) => {
  event.preventDefault()
  const dragData = event.dataTransfer.getData('application/json')
  if (dragData) {
    const data = JSON.parse(dragData)
    if (data.type === 'question' && data.id !== props.question.id) {
      isDragOver.value = true
    }
  }
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const dragData = event.dataTransfer.getData('application/json')
  if (dragData) {
    const data = JSON.parse(dragData)
    if (data.type === 'question' && data.id !== props.question.id) {
      emit('question-reorder', {
        questionId: data.id,
        targetQuestionId: props.question.id,
        targetOrder: props.question.order
      })
    }
  }
}
</script>

<style scoped>
.question-builder {
  transition: all 0.2s ease-in-out;
}

.question-builder:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.question-builder.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.question-builder.drag-over {
  border-color: #3b82f6;
  background-color: #eff6ff;
  transform: translateY(-2px);
}

.question-drag-handle:hover {
  transform: scale(1.1);
}

.question-settings {
  animation: slideDown 0.2s ease-in-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

input:focus,
textarea:focus {
  outline: none;
}

.question-type-badge {
  white-space: nowrap;
}
</style>