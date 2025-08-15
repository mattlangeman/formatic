<template>
  <div class="page-builder bg-white rounded-lg border border-gray-200 shadow-sm">
    <!-- Page Header -->
    <div class="page-header p-4 border-b border-gray-200 bg-gray-50">
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-3">
          <div class="page-drag-handle cursor-move p-1 text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
            </svg>
          </div>
          
          <div class="flex-1">
            <input
              v-model="editablePage.name"
              @blur="updatePage"
              @keyup.enter="updatePage"
              class="text-lg font-medium text-gray-900 bg-transparent border-none p-0 focus:ring-2 focus:ring-blue-500 rounded"
              placeholder="Page name"
            />
            <div class="text-sm text-gray-500 mt-1">
              {{ totalItemsCount }} item{{ totalItemsCount !== 1 ? 's' : '' }} 
              ({{ page.questions?.length || 0 }} questions, {{ page.question_groups?.length || 0 }} groups)
            </div>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <button
            @click="togglePageSettings"
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            title="Page settings"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
          
          <button
            @click="deletePage"
            class="p-2 text-red-400 hover:text-red-600 rounded-lg hover:bg-red-50"
            title="Delete page"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Page Settings Panel (collapsible) -->
      <div v-if="showPageSettings" class="mt-4 pt-4 border-t border-gray-200">
        <div class="space-y-4">
          <!-- Basic Settings Row -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Page Slug</label>
              <input
                v-model="editablePage.slug"
                @blur="updatePage"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Page Order</label>
              <input
                v-model.number="editablePage.order"
                @blur="updatePage"
                type="number"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <!-- Tag Settings Section -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3 flex items-center">
              <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              Tag Settings
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tag Text</label>
                <input
                  v-model="editablePage.tag_text"
                  @blur="updatePage"
                  placeholder="e.g., Premium, Beta, New"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p class="text-xs text-gray-500 mt-1">Text displayed in the tag/pill</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tag Hover Text</label>
                <textarea
                  v-model="editablePage.tag_hover_text"
                  @blur="updatePage"
                  placeholder="e.g., Upgrading to premium allows for additional analysis"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">Text shown when hovering over the tag</p>
              </div>
            </div>

            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Tag Display Condition</label>
              <div class="bg-gray-50 rounded-md p-3">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Field</label>
                    <input
                      v-model="tagConditionField"
                      @blur="updateTagCondition"
                      placeholder="e.g., tool_mode"
                      class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Operator</label>
                    <select 
                      v-model="tagConditionOperator"
                      @change="updateTagCondition"
                      class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      <option value="equals">equals</option>
                      <option value="not_equals">not equals</option>
                      <option value="in">in list</option>
                      <option value="not_in">not in list</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Value</label>
                    <input
                      v-model="tagConditionValue"
                      @blur="updateTagCondition"
                      placeholder="e.g., free"
                      class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <p class="text-xs text-gray-500 mt-2">Tag will be displayed when this condition is met</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Questions Area -->
    <div class="questions-area p-4">
      <div 
        @drop="handleDrop"
        @dragover.prevent
        @dragenter="handleDragEnter"
        @dragleave="handleDragLeave"
        class="questions-container min-h-48"
        :class="{ 'drag-over': isDragOver }"
      >
        <!-- Unified Questions and Groups (sorted by order) -->
        <div v-if="sortedPageItems.length > 0" class="space-y-4">
          <template v-for="item in sortedPageItems" :key="item.type + '-' + item.item.id">
            <!-- Question Group -->
            <QuestionGroupBuilder
              v-if="item.type === 'group'"
              :group="item.item"
              :form-slug="formSlug"
              :page-id="page.id"
              :question-types="questionTypes"
              @group-updated="handleGroupUpdated"
              @group-deleted="handleGroupDeleted"
              @question-added="handleGroupQuestionAdded"
              @question-updated="handleGroupQuestionUpdated"
              @question-deleted="handleGroupQuestionDeleted"
              @group-reorder="handleGroupReorder"
            />
            
            <!-- Individual Question -->
            <QuestionBuilder
              v-else-if="item.type === 'question'"
              :question="item.item"
              :question-types="questionTypes"
              :page-id="page.id"
              :form-slug="formSlug"
              @question-updated="$emit('question-updated', page.id, item.item.id, $event)"
              @question-deleted="$emit('question-deleted', page.id, item.item.id)"
              @question-added="$emit('question-added', page.id, $event)"
              @question-reorder="handleQuestionReorder"
            />
          </template>
        </div>
        
        <!-- Empty state -->
        <div v-if="!hasAnyContent" class="empty-questions-area">
          <div class="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
            <svg class="mx-auto h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="mt-4 text-sm font-medium text-gray-900">No content yet</h4>
            <p class="mt-2 text-xs text-gray-500">Drag question types or question groups here to add them to this page</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { formBuilderApi } from '../services/api.js'
import QuestionBuilder from './QuestionBuilder.vue'
import QuestionGroupBuilder from './QuestionGroupBuilder.vue'

// Props
const props = defineProps({
  page: {
    type: Object,
    required: true
  },
  formSlug: {
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
  'page-updated',
  'page-deleted', 
  'question-added',
  'question-updated',
  'question-deleted',
  'questions-reordered',
  'group-added',
  'group-updated',
  'group-deleted',
  'groups-reordered'
])

// Reactive data
const editablePage = ref({ ...props.page })
const showPageSettings = ref(false)
const isDragOver = ref(false)

// Tag condition reactive data
const tagConditionField = ref('')
const tagConditionOperator = ref('equals')
const tagConditionValue = ref('')

// Computed properties
const totalItemsCount = computed(() => {
  return (props.page.questions?.length || 0) + (props.page.question_groups?.length || 0)
})

const hasAnyContent = computed(() => {
  return totalItemsCount.value > 0
})

// Create a unified, sorted array of all page items (questions and groups)
const sortedPageItems = computed(() => {
  const items = []
  
  // Add individual questions
  if (props.page.questions) {
    props.page.questions.forEach(question => {
      items.push({
        type: 'question',
        order: question.order || 0,
        item: question
      })
    })
  }
  
  // Add question groups
  if (props.page.question_groups) {
    props.page.question_groups.forEach(group => {
      items.push({
        type: 'group',
        order: group.order || 0,
        item: group
      })
    })
  }
  
  // Sort by order
  return items.sort((a, b) => a.order - b.order)
})

// Watch for prop changes
watch(() => props.page, (newPage) => {
  editablePage.value = { ...newPage }
  initializeTagCondition()
}, { deep: true })

// Initialize tag condition fields from page data
const initializeTagCondition = () => {
  const condition = props.page.tag_display_condition || {}
  
  if (condition.field && condition.operator && condition.value !== undefined) {
    tagConditionField.value = condition.field
    tagConditionOperator.value = condition.operator
    tagConditionValue.value = condition.value
  } else {
    tagConditionField.value = ''
    tagConditionOperator.value = 'equals'
    tagConditionValue.value = ''
  }
}

// Initialize on component mount
initializeTagCondition()

// Update page
const updatePage = async () => {
  try {
    const response = await formBuilderApi.updatePage(
      props.formSlug,
      props.page.id,
      {
        name: editablePage.value.name,
        slug: editablePage.value.slug,
        tag_text: editablePage.value.tag_text || '',
        tag_hover_text: editablePage.value.tag_hover_text || '',
        tag_display_condition: editablePage.value.tag_display_condition || {},
        config: editablePage.value.config || {},
        conditional_logic: editablePage.value.conditional_logic || {},
        disabled_condition: editablePage.value.disabled_condition || {}
      }
    )
    emit('page-updated', response.data)
  } catch (error) {
    console.error('Failed to update page:', error)
  }
}

// Update tag condition based on UI inputs
const updateTagCondition = () => {
  if (tagConditionField.value && tagConditionValue.value) {
    editablePage.value.tag_display_condition = {
      field: tagConditionField.value,
      operator: tagConditionOperator.value,
      value: tagConditionValue.value
    }
  } else {
    editablePage.value.tag_display_condition = {}
  }
  updatePage()
}

// Delete page
const deletePage = async () => {
  if (confirm(`Are you sure you want to delete "${props.page.name}" and all its questions?`)) {
    try {
      await formBuilderApi.deletePage(props.formSlug, props.page.id)
      emit('page-deleted', props.page.id)
    } catch (error) {
      console.error('Failed to delete page:', error)
    }
  }
}

// Toggle page settings
const togglePageSettings = () => {
  showPageSettings.value = !showPageSettings.value
}

// Drag and drop handlers
const handleDrop = async (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  // Check for question type
  const questionTypeData = event.dataTransfer.getData('application/json')
  if (questionTypeData) {
    const questionType = JSON.parse(questionTypeData)
    await addQuestion(questionType)
    return
  }
  
  // Check for group type (template)
  const groupTypeData = event.dataTransfer.getData('text/group-type')
  if (groupTypeData) {
    const template = JSON.parse(groupTypeData)
    await addQuestionGroup(template)
    return
  }
}

// Add new question
const addQuestion = async (questionType) => {
  try {
    // Generate default question data based on type
    const questionData = {
      type_slug: questionType.slug,
      name: `${questionType.name} Question`,
      slug: `${questionType.slug}-${Date.now()}`,
      text: `${questionType.name} question`,
      subtext: '',
      required: false,
      config: questionType.config || {},
      validation: {},
      conditional_logic: {}
    }
    
    const response = await formBuilderApi.createQuestion(
      props.formSlug,
      props.page.id,
      questionData
    )
    
    emit('question-added', props.page.id, response.data)
  } catch (error) {
    console.error('Failed to add question:', error)
  }
}

// Add new question group
const addQuestionGroup = async (template) => {
  try {
    const groupData = {
      name: template.name,
      template_slug: template.slug
    }
    
    const response = await formBuilderApi.createQuestionGroup(
      props.formSlug,
      props.page.id,
      groupData
    )
    
    emit('group-added', props.page.id, response.data)
  } catch (error) {
    console.error('Failed to add question group:', error)
  }
}

// Handle drag events
const handleDragEnter = () => {
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  // Only set to false if we're leaving the container, not entering a child
  if (!event.currentTarget.contains(event.relatedTarget)) {
    isDragOver.value = false
  }
}

// Handle question reordering
const handleQuestionReorder = async (reorderData) => {
  try {
    const { questionId, targetQuestionId, targetOrder } = reorderData
    
    // Find the questions in the current page
    const draggedQuestion = props.page.questions.find(q => q.id === questionId)
    const targetQuestion = props.page.questions.find(q => q.id === targetQuestionId)
    
    if (!draggedQuestion || !targetQuestion) {
      console.error('Could not find questions for reordering')
      return
    }
    
    // Create a new array with reordered questions
    const questions = [...props.page.questions]
    const draggedIndex = questions.findIndex(q => q.id === questionId)
    const targetIndex = questions.findIndex(q => q.id === targetQuestionId)
    
    // Remove the dragged question and insert it at the target position
    questions.splice(draggedIndex, 1)
    questions.splice(targetIndex, 0, draggedQuestion)
    
    // Update the orders for all questions
    const questionOrders = questions.map((question, index) => ({
      id: question.id,
      order: index + 1
    }))
    
    // Call the API to update the order
    await formBuilderApi.reorderQuestions(props.formSlug, props.page.id, questionOrders)
    
    // Emit the reordered questions to the parent
    emit('questions-reordered', props.page.id, questions.map((q, index) => ({ ...q, order: index + 1 })))
    
  } catch (error) {
    console.error('Failed to reorder questions:', error)
  }
}

// Question Group Event Handlers
const handleGroupUpdated = (updatedGroup) => {
  emit('group-updated', props.page.id, updatedGroup)
}

const handleGroupDeleted = (groupId) => {
  emit('group-deleted', props.page.id, groupId)
}

const handleGroupQuestionAdded = (newQuestion) => {
  // Refresh the page data to show the new question in the group
  emit('question-added', props.page.id, newQuestion)
}

const handleGroupQuestionUpdated = (updatedQuestion) => {
  emit('question-updated', props.page.id, updatedQuestion.id, updatedQuestion)
}

const handleGroupQuestionDeleted = (questionId) => {
  emit('question-deleted', props.page.id, questionId)
}

// Handle question group reordering within mixed content
const handleGroupReorder = async (reorderData) => {
  try {
    const { draggedGroupId, targetGroupId } = reorderData
    
    // Find the dragged group and target group in the current page
    const draggedGroup = props.page.question_groups.find(g => g.id === draggedGroupId)
    const targetGroup = props.page.question_groups.find(g => g.id === targetGroupId)
    
    if (!draggedGroup || !targetGroup) {
      console.error('Could not find groups for reordering')
      return
    }
    
    // Get the target group's order to determine new position
    const targetOrder = targetGroup.order
    
    // Find what order the dragged group should have
    // If dragging down, place after target. If dragging up, place before target.
    const draggedCurrentOrder = draggedGroup.order
    let newOrder
    
    if (draggedCurrentOrder < targetOrder) {
      // Dragging down - place after target
      newOrder = targetOrder + 0.5
    } else {
      // Dragging up - place before target  
      newOrder = targetOrder - 0.5
    }
    
    // Update the dragged group's order
    draggedGroup.order = newOrder
    
    // Normalize all orders to be sequential integers
    const allItems = [...sortedPageItems.value]
    allItems.forEach((item, index) => {
      const newSequentialOrder = index + 1
      if (item.type === 'question') {
        item.item.order = newSequentialOrder
      } else if (item.type === 'group') {
        item.item.order = newSequentialOrder
      }
    })
    
    // Prepare API calls for both questions and groups
    const questionOrders = props.page.questions.map(q => ({
      id: q.id,
      order: q.order
    }))
    
    const groupOrders = props.page.question_groups.map(g => ({
      id: g.id,
      order: g.order
    }))
    
    // Call both APIs to update orders
    await Promise.all([
      formBuilderApi.reorderQuestions(props.formSlug, props.page.id, questionOrders),
      formBuilderApi.reorderQuestionGroups(props.formSlug, props.page.id, groupOrders)
    ])
    
    // Emit updates to parent
    emit('groups-reordered', props.page.id, props.page.question_groups)
    emit('questions-reordered', props.page.id, props.page.questions)
    
  } catch (error) {
    console.error('Failed to reorder question groups:', error)
  }
}
</script>

<style scoped>
.page-builder {
  transition: all 0.2s ease-in-out;
}

.questions-container {
  transition: background-color 0.2s ease-in-out;
}

.questions-container.drag-over {
  background-color: #eff6ff;
  border: 2px dashed #3b82f6;
  border-radius: 8px;
}

.empty-questions-area {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-drag-handle:hover {
  transform: scale(1.1);
}

.page-header input:focus {
  outline: none;
}
</style>