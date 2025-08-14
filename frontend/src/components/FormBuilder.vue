<template>
  <div class="form-builder">
    <!-- Header -->
    <div class="form-builder-header bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-4">
            <button 
              @click="$router.go(-1)"
              class="text-gray-600 hover:text-gray-900"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
              </svg>
            </button>
            <div>
              <h1 class="text-xl font-semibold text-gray-900">
                {{ form?.name || 'Form Builder' }}
              </h1>
              <p class="text-sm text-gray-500" v-if="form?.slug">
                {{ form?.slug }}
              </p>
            </div>
          </div>
          
          <div class="flex items-center space-x-3">
            <button 
              @click="previewForm"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              Preview
            </button>
            
            <button 
              @click="publishForm"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
              </svg>
              Publish
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="form-builder-content flex h-screen">
      <!-- Question Types Palette -->
      <div class="question-palette w-80 bg-gray-50 border-r border-gray-200 overflow-y-auto">
        <div class="p-4">
          <!-- Question Groups Section -->
          <div class="mb-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Question Groups</h3>
            <div class="space-y-2">
              <div 
                v-for="template in groupTemplates" 
                :key="template.slug"
                @dragstart="startGroupDrag($event, template)"
                @dragend="endDrag"
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

          <!-- Question Types Section -->
          <div>
            <h2 class="text-lg font-medium text-gray-900 mb-4">Question Types</h2>
            
            <div class="space-y-2">
              <div 
                v-for="questionType in questionTypes" 
                :key="questionType.id"
                @dragstart="startDrag($event, questionType)"
                @dragend="endDrag"
                draggable="true"
                class="question-type-item p-3 bg-white rounded-lg border border-gray-200 cursor-move hover:border-blue-300 hover:shadow-sm transition-all"
              >
                <div class="flex items-center space-x-3">
                  <div class="question-type-icon w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <component :is="getQuestionTypeIcon(questionType.slug)" class="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">{{ questionType.name }}</h3>
                    <p class="text-xs text-gray-500">{{ questionType.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Canvas -->
      <div class="form-canvas flex-1 overflow-y-auto">
        <div v-if="isLoading" class="max-w-4xl mx-auto p-6 flex items-center justify-center h-full">
          <div class="text-center">
            <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-blue-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-gray-600">Loading form...</p>
          </div>
        </div>
        <div v-else-if="form" class="max-w-4xl mx-auto p-6">
          <!-- Form Settings Panel -->
          <div class="form-settings mb-8 bg-white rounded-lg border border-gray-200 p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Form Settings</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Form Name</label>
                <input 
                  v-model="form.name"
                  @input="markAsChanged"
                  type="text" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Slug</label>
                <input 
                  v-model="form.slug"
                  @input="markAsChanged"
                  type="text" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Pages -->
          <div class="pages-container">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-gray-900">Pages</h3>
              <button 
                @click="addPage"
                class="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm bg-green-600 text-sm font-medium text-white hover:bg-green-700"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
                Add Page
              </button>
            </div>
            
            <div v-if="form.pages && form.pages.length > 0" class="space-y-6">
              <PageBuilder
                v-for="page in form.pages"
                :key="page.id"
                :page="page"
                :form-slug="form.slug"
                :question-types="questionTypes"
                @page-updated="handlePageUpdate"
                @page-deleted="handlePageDelete"
                @question-added="handleQuestionAdded"
                @question-updated="handleQuestionUpdate"
                @question-deleted="handleQuestionDelete"
                @questions-reordered="handleQuestionsReorder"
                @group-added="handleGroupAdded"
                @group-updated="handleGroupUpdate"
                @group-deleted="handleGroupDelete"
                @groups-reordered="handleGroupsReorder"
              />
            </div>
            
            <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <h3 class="mt-4 text-lg font-medium text-gray-900">No pages yet</h3>
              <p class="mt-2 text-sm text-gray-500">Get started by adding your first page.</p>
              <button 
                @click="addPage"
                class="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700"
              >
                Add First Page
              </button>
            </div>
          </div>
        </div>
        <div v-else class="max-w-4xl mx-auto p-6 flex items-center justify-center h-full">
          <div class="text-center">
            <svg class="mx-auto h-12 w-12 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Form not found</h3>
            <p class="text-sm text-gray-500">The form could not be loaded.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <PublishModal 
      v-if="showPublishModal"
      :form="form"
      @publish="handlePublish"
      @close="showPublishModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { formBuilderApi, questionTypesApi, questionGroupTemplatesApi, formApi } from '../services/api.js'
import PageBuilder from './PageBuilder.vue'
import PublishModal from './PublishModal.vue'

const route = useRoute()
const router = useRouter()

// Reactive data
const form = ref(null)
const questionTypes = ref([])
const groupTemplates = ref([])
const hasChanges = ref(false)
const showPublishModal = ref(false)
const draggedQuestionType = ref(null)
const isLoading = ref(true)

// Get form slug from route
const formSlug = computed(() => route.params.slug)

// Load form and question types
onMounted(async () => {
  await Promise.all([
    loadQuestionTypes(),
    loadGroupTemplates()
  ])
  
  if (formSlug.value) {
    await loadForm()
  } else {
    isLoading.value = false
  }
})

// Load question types from API
const loadQuestionTypes = async () => {
  try {
    const response = await questionTypesApi.getQuestionTypes()
    questionTypes.value = response.data
  } catch (error) {
    console.error('Failed to load question types:', error)
  }
}

// Load group templates from API
const loadGroupTemplates = async () => {
  try {
    const response = await questionGroupTemplatesApi.getTemplates()
    groupTemplates.value = response.data
  } catch (error) {
    console.error('Failed to load group templates:', error)
  }
}

// Load form data
const loadForm = async () => {
  try {
    const response = await formBuilderApi.getBuilderForm(formSlug.value)
    form.value = response.data
  } catch (error) {
    console.error('Failed to load form:', error)
    router.push('/')
  } finally {
    isLoading.value = false
  }
}

// Mark form as changed
const markAsChanged = () => {
  hasChanges.value = true
}

// Question type icons mapping
const getQuestionTypeIcon = (slug) => {
  const iconMap = {
    'short-text': 'AlignLeftIcon',
    'number': 'HashIcon',
    'dropdown': 'ChevronDownIcon',
    'yes-no': 'CheckCircleIcon',
    'address': 'LocationMarkerIcon'
  }
  
  return iconMap[slug] || 'QuestionMarkCircleIcon'
}

// Drag and drop handlers
const startDrag = (event, questionType) => {
  draggedQuestionType.value = questionType
  event.dataTransfer.setData('application/json', JSON.stringify(questionType))
  event.dataTransfer.effectAllowed = 'copy'
}

const endDrag = () => {
  draggedQuestionType.value = null
}

// Group drag handlers
const startGroupDrag = (event, template) => {
  event.dataTransfer.setData('text/group-type', JSON.stringify(template))
  event.dataTransfer.effectAllowed = 'copy'
}

// Page management
const addPage = async () => {
  try {
    const pageData = {
      name: `Page ${form.value.pages.length + 1}`,
      slug: `page-${form.value.pages.length + 1}`,
      config: {},
      conditional_logic: {}
    }
    
    const response = await formBuilderApi.createPage(form.value.slug, pageData)
    form.value.pages.push(response.data)
    markAsChanged()
  } catch (error) {
    console.error('Failed to add page:', error)
  }
}

// Event handlers
const handlePageUpdate = (updatedPage) => {
  const pageIndex = form.value.pages.findIndex(p => p.id === updatedPage.id)
  if (pageIndex !== -1) {
    form.value.pages[pageIndex] = updatedPage
    markAsChanged()
  }
}

const handlePageDelete = (pageId) => {
  form.value.pages = form.value.pages.filter(p => p.id !== pageId)
  markAsChanged()
}

const handleQuestionAdded = (pageId, question) => {
  const page = form.value.pages.find(p => p.id === pageId)
  if (page) {
    page.questions.push(question)
    markAsChanged()
  }
}

const handleQuestionUpdate = (pageId, questionId, updatedQuestion) => {
  const page = form.value.pages.find(p => p.id === pageId)
  if (page) {
    const questionIndex = page.questions.findIndex(q => q.id === questionId)
    if (questionIndex !== -1) {
      page.questions[questionIndex] = updatedQuestion
      markAsChanged()
    }
  }
}

const handleQuestionDelete = (pageId, questionId) => {
  const page = form.value.pages.find(p => p.id === pageId)
  if (page) {
    page.questions = page.questions.filter(q => q.id !== questionId)
    markAsChanged()
  }
}

const handleQuestionsReorder = (pageId, questions) => {
  const page = form.value.pages.find(p => p.id === pageId)
  if (page) {
    page.questions = questions
    markAsChanged()
  }
}

// Question Group Event Handlers
const handleGroupAdded = async (pageId, newGroup) => {
  // Add group to local state immediately
  const pageIndex = form.value.pages.findIndex(p => p.id === pageId)
  if (pageIndex !== -1) {
    if (!form.value.pages[pageIndex].question_groups) {
      form.value.pages[pageIndex].question_groups = []
    }
    form.value.pages[pageIndex].question_groups.push(newGroup)
    markAsChanged()
  }
}

const handleGroupUpdate = async (pageId, updatedGroup) => {
  const pageIndex = form.value.pages.findIndex(p => p.id === pageId)
  if (pageIndex !== -1) {
    const groupIndex = form.value.pages[pageIndex].question_groups?.findIndex(g => g.id === updatedGroup.id)
    if (groupIndex !== -1) {
      form.value.pages[pageIndex].question_groups[groupIndex] = updatedGroup
      markAsChanged()
    }
  }
}

const handleGroupDelete = async (pageId, groupId) => {
  const pageIndex = form.value.pages.findIndex(p => p.id === pageId)
  if (pageIndex !== -1) {
    form.value.pages[pageIndex].question_groups = form.value.pages[pageIndex].question_groups?.filter(g => g.id !== groupId) || []
    markAsChanged()
  }
}

const handleGroupsReorder = (pageId, groups) => {
  const page = form.value.pages.find(p => p.id === pageId)
  if (page) {
    page.question_groups = groups
    markAsChanged()
  }
}

// Form actions
const previewForm = () => {
  // Open form in new tab/window for preview
  window.open(`/form/${form.value.slug}`, '_blank')
}

const publishForm = () => {
  showPublishModal.value = true
}

const handlePublish = async (publishData) => {
  try {
    await formApi.createVersion(form.value.slug, {
      notes: publishData.notes,
      created_by: publishData.createdBy,
      is_published: true
    })
    
    hasChanges.value = false
    showPublishModal.value = false
    
    // Show success message
    alert('Form published successfully!')
  } catch (error) {
    console.error('Failed to publish form:', error)
    alert('Failed to publish form. Please try again.')
  }
}
</script>

<style scoped>
.form-builder {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.form-builder-content {
  flex: 1;
  overflow: hidden;
}

.question-type-item {
  transition: all 0.2s ease-in-out;
}

.question-type-item:hover {
  transform: translateY(-1px);
}

.question-type-item.dragging {
  opacity: 0.5;
}

.form-canvas {
  background-color: #f8fafc;
}

.pages-container {
  min-height: 400px;
}
</style>