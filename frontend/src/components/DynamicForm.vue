<template>
  <div class="form-container">
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading form...</p>
    </div>

    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-600 mb-4">
        <svg class="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.96-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <p class="text-red-600 font-medium">{{ error }}</p>
    </div>

    <div v-else-if="form">
      <div class="form-header">
        <h1 class="form-title">{{ form.name }}</h1>
        <p v-if="form.description" class="form-description">{{ form.description }}</p>
      </div>

      <div v-if="!isFormReady" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Preparing form...</p>
      </div>

      <!-- Completion Status Display -->
      <div v-if="isComplete" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <div>
            <p class="text-green-800 font-medium">Form Completed</p>
            <p v-if="completedDateTime" class="text-green-600 text-sm">
              Submitted on {{ new Date(completedDateTime).toLocaleDateString() + ' ' + new Date(completedDateTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
            </p>
          </div>
        </div>
      </div>

      <FormKit
        v-else
        type="form"
        :key="`form-${submissionId}`"
        :actions="false"
        @submit="handleSubmit"
        :disabled="isFormDisabled"
      >
        <div v-for="page in visiblePages" :key="page.id" class="mb-8">
          <!-- Multi-page forms: show page name with switch link -->
          <div v-if="form.pages.length > 1" class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <h2 class="text-xl font-semibold text-gray-900">
                {{ page.name }}
              </h2>
              <TagPill
                :text="page.tag_text"
                :hover-text="page.tag_hover_text"
                :display-condition="page.tag_display_condition"
                :form-data="formData"
                variant="primary"
                size="sm"
              />
            </div>
            <router-link
              :to="getTableViewUrl()"
              class="text-sm text-primary-600 hover:text-primary-800 transition-colors inline-flex items-center"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0V4a2 2 0 012-2h14a2 2 0 012 2v16a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              Switch to Table View
            </router-link>
          </div>

          <!-- Single-page forms: show tag and switch link -->
          <div v-else class="flex justify-between items-center mb-4">
            <TagPill
              :text="page.tag_text"
              :hover-text="page.tag_hover_text"
              :display-condition="page.tag_display_condition"
              :form-data="formData"
              variant="primary"
              size="sm"
            />
            <router-link
              :to="getTableViewUrl()"
              class="text-sm text-primary-600 hover:text-primary-800 transition-colors inline-flex items-center"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0V4a2 2 0 012-2h14a2 2 0 012 2v16a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              Switch to Table View
            </router-link>
          </div>

          <div class="space-y-6">
            <div v-for="question in visibleQuestions(page)" :key="question.id">
              <!-- Special handling for complex question types like address -->
              <div v-if="isComplexQuestionType(question)">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  {{ question.text }}
                  <span v-if="question.required" class="text-red-500 ml-1" style="color: #ef4444;">*</span>
                </label>
                <p v-if="question.subtext" class="text-sm text-gray-600 mb-3">{{ question.subtext }}</p>
                <AddressInput
                  :name="question.slug"
                  :question-type-config="getQuestionTypeConfig(question)"
                  :form-data="formData"
                  :update-field="updateField"
                  :parent-required="question.required"
                />
              </div>

              <!-- Special handling for disabled select fields -->
              <div v-else-if="isDisabledSelect(question, page)">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  <span v-html="getFormattedLabel(question)"></span>
                </label>
                <p v-if="question.subtext" class="text-sm text-gray-600 mb-3">{{ question.subtext }}</p>
                <DisabledSelectView
                  :form-kit-type="getFormKitType(question)"
                  :name="question.slug"
                  :model-value="formData[question.slug]"
                  :options="getQuestionOptions(question)"
                  :multiple="question.config?.multiple"
                  :required="getQuestionRequired(question)"
                  :placeholder="getQuestionPlaceholder(question)"
                />
              </div>

              <!-- Normal field handling for radio/checkbox with special labels -->
              <div v-else-if="isRadioOrCheckbox(question)">
                <!-- Custom wrapper for radio/checkbox to preserve option labels -->
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  <span v-html="getFormattedLabel(question)"></span>
                </label>
                <p v-if="question.subtext" class="text-sm text-gray-600 mb-3">{{ question.subtext }}</p>
                <FormKit
                  :type="getFormKitType(question)"
                  :name="question.slug"
                  :model-value="formData[question.slug]"
                  @update:model-value="(value) => updateField(question.slug, value)"
                  :validation="getValidationRules(question)"
                  :options="getQuestionOptions(question)"
                  :multiple="question.config?.multiple"
                  :required="getQuestionRequired(question)"
                  :disabled="isComplete"
                  :label="false"
                />
              </div>

              <!-- Standard FormKit fields for everything else -->
              <FormKit
                v-else
                :type="getFormKitType(question)"
                :name="question.slug"
                :model-value="formData[question.slug]"
                @update:model-value="(value) => updateField(question.slug, value)"
                :help="question.subtext"
                :validation="getValidationRules(question)"
                :placeholder="getQuestionPlaceholder(question)"
                :options="getQuestionOptions(question)"
                :multiple="question.config?.multiple"
                :required="question.required"
                :disabled="isComplete"
              >
                <template #label>
                  <span v-html="getFormattedLabel(question)"></span>
                </template>
              </FormKit>
            </div>
          </div>
        </div>

        <div class="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
          <button
            v-if="currentPage > 0"
            type="button"
            @click="previousPage"
            class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Previous
          </button>

          <div v-if="form.pages.length > 1" class="flex space-x-2">
            <button
              v-for="(page, index) in form.pages"
              :key="page.id"
              type="button"
              @click.prevent="navigateToPage(index)"
              :disabled="!canNavigateToPage(index)"
              class="w-3 h-3 rounded-full transition-colors duration-200"
              :class="[
                index === currentPage ? 'bg-primary-600' : canNavigateToPage(index) ? 'bg-primary-400 hover:bg-primary-500 cursor-pointer' : 'bg-gray-300 cursor-not-allowed'
              ]"
              :title="`${page.name} ${canNavigateToPage(index) ? '(click to navigate)' : '(complete previous pages first)'}`"
            ></button>
          </div>

          <FormKit
            v-if="isLastPage && !isComplete"
            type="submit"
            :disabled="submitting"
          >
            {{ submitting ? 'Submitting...' : 'Submit' }}
          </FormKit>

          <button
            v-else-if="!isComplete"
            type="button"
            @click="nextPage"
            :disabled="!isCurrentPageValid"
            :class="[
              'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2',
              isCurrentPageValid
                ? 'text-white bg-primary-600 hover:bg-primary-700 focus:ring-primary-500'
                : 'text-gray-400 bg-gray-300 cursor-not-allowed'
            ]"
          >
            Next
            <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </FormKit>

      <!-- Success Message -->
      <div v-if="submitted" class="mt-8 p-6 bg-green-50 border border-green-200 rounded-md">
        <div class="flex">
          <svg class="h-5 w-5 text-green-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-green-800">Form submitted successfully!</h3>
            <p class="mt-1 text-sm text-green-700">Thank you for your response.</p>
            <div class="mt-4 flex gap-3">
              <router-link
                :to="{ name: 'submissions', params: { slug: formSlug } }"
                class="text-sm font-medium text-green-700 hover:text-green-600"
              >
                View all submissions →
              </router-link>
              <button
                @click="startNewSubmission"
                class="text-sm font-medium text-green-700 hover:text-green-600"
              >
                Submit another response →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { formApi, submissionApi, questionTypesApi } from '../services/api'
import AddressInput from './AddressInput.vue'
import DisabledSelectView from './DisabledSelectView.vue'
import TagPill from './TagPill.vue'
import { useConditionalLogic } from '../composables/useConditionalLogic.js'
import { useAddressField } from '../composables/useAddressField.js'

// Debounce utility function
const debounce = (fn, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(null, args), delay)
  }
}

export default {
  name: 'DynamicForm',
  components: {
    AddressInput,
    DisabledSelectView,
    TagPill
  },
  props: {
    formSlug: {
      type: String,
      required: true
    }
  },
  setup(props, { emit }) {
    const route = useRoute()
    const router = useRouter()
    const form = ref(null)
    const formData = ref({})
    const questionTypes = ref({})
    const loading = ref(true)
    const error = ref(null)
    const submitting = ref(false)
    const submitted = ref(false)
    const currentPage = ref(0)
    const submissionId = ref(null)
    const isInitializing = ref(true)
    const completedPages = ref(new Set())
    const isComplete = ref(false)
    const completedDateTime = ref(null)
    const isUpdatingUrl = ref(false)
    const isLoadingForm = ref(false)

    // Use conditional logic composable
    const { isQuestionDisabled } = useConditionalLogic()

    const visiblePages = computed(() => {
      if (!form.value) return []
      return form.value.pages.filter((_, index) => {
        if (form.value.pages.length === 1) return true
        return index === currentPage.value
      })
    })

    const isLastPage = computed(() => {
      return currentPage.value === form.value?.pages.length - 1
    })

    const currentPageData = computed(() => {
      return form.value?.pages?.[currentPage.value] || null
    })

    // Computed to get current page by slug from URL or default to first page
    const getCurrentPageFromRoute = () => {
      if (!form.value?.pages?.length) return 0

      const pageSlug = route.params.pageSlug
      if (!pageSlug) return 0

      const pageIndex = form.value.pages.findIndex(page => page.slug === pageSlug)
      return pageIndex >= 0 ? pageIndex : 0
    }

    const canNavigateToPage = (pageIndex) => {
      // Can always navigate to first page
      if (pageIndex === 0) return true

      // Can ONLY navigate to a page if ALL previous pages are completed
      // This ensures sequential completion is enforced
      for (let i = 0; i < pageIndex; i++) {
        if (!completedPages.value.has(i)) {
          return false
        }
      }

      return true
    }

    const recalculatePageCompletion = () => {
      if (!form.value?.pages) return

      const newCompletedPages = new Set()

      // Check each page to see if all required questions are answered
      form.value.pages.forEach((page, pageIndex) => {
        if (isPageComplete(pageIndex)) {
          newCompletedPages.add(pageIndex)
        }
      })

      const oldCompletedPages = new Set(completedPages.value)

      // Log changes for debugging
      const newlyCompleted = [...newCompletedPages].filter(i => !oldCompletedPages.has(i))
      const newlyIncomplete = [...oldCompletedPages].filter(i => !newCompletedPages.has(i))

      if (newlyCompleted.length > 0) {
        console.log('🎉 Newly completed pages:', newlyCompleted.map(i => i + 1))
      }
      if (newlyIncomplete.length > 0) {
        console.log('⚠️ Pages became incomplete:', newlyIncomplete.map(i => i + 1))
      }

      // Update the completed pages
      completedPages.value = newCompletedPages
    }

    const isPageComplete = (pageIndex) => {
      if (!form.value?.pages?.[pageIndex]) return false

      const page = form.value.pages[pageIndex]
      const allQuestions = visibleQuestions(page)

      for (const question of allQuestions) {
        const logic = evaluateConditionalLogic(question, formData.value)
        if (logic.required) {
          if (isComplexQuestionType(question)) {
            // For complex fields like address, check all required sub-fields
            const complexFieldNames = getComplexFieldNames(question)

            for (const fieldName of complexFieldNames) {
              const flatKey = `${question.slug}__${fieldName}`
              const value = formData.value[flatKey]

              // Check for empty values - includes undefined, null, empty string, or whitespace-only string
              const isEmpty = value === undefined ||
                             value === null ||
                             value === '' ||
                             (typeof value === 'string' && value.trim() === '')

              if (isEmpty) {
                return false
              }
            }
          } else {
            // For simple fields
            const value = formData.value[question.slug]

            // Check for empty values - includes undefined, null, empty string, or whitespace-only string
            const isEmpty = value === undefined ||
                           value === null ||
                           value === '' ||
                           (typeof value === 'string' && value.trim() === '')

            if (isEmpty) {
              return false
            }
          }
        }
      }

      return true
    }

    const navigateToPage = (pageIndex, replace = false) => {
      if (!form.value?.pages?.[pageIndex] || !canNavigateToPage(pageIndex)) {
        return false
      }

      const page = form.value.pages[pageIndex]

      // Determine the correct route based on whether we have a submission ID
      let routeName, routeParams

      if (submissionId.value) {
        // We have a submission - use submission-specific routes
        routeName = 'form-submission-page'
        routeParams = {
          slug: props.formSlug,
          submissionId: submissionId.value,
          pageSlug: page.slug
        }
      } else {
        // No submission yet - use regular form routes
        routeName = 'form-page'
        routeParams = {
          slug: props.formSlug,
          pageSlug: page.slug
        }
      }

      if (replace) {
        router.replace({ name: routeName, params: routeParams })
      } else {
        router.push({ name: routeName, params: routeParams })
      }

      return true
    }

    const isFormReady = computed(() => {
      return form.value && submissionId.value && Object.keys(formData.value).length > 0 && Object.keys(questionTypes.value).length > 0
    })

    const isFormDisabled = computed(() => {
      return submitting.value || isComplete.value
    })

    const isCurrentPageValid = computed(() => {
      if (!currentPageData.value) return true

      // Force reactivity by accessing formData.value first
      const currentFormData = formData.value

      console.log('🔍 Validating current page:', currentPage.value)
      
      const allQuestions = visibleQuestions(currentPageData.value)
      for (const question of allQuestions) {
        if (question.required) {
          if (isComplexQuestionType(question)) {
            // For complex fields like address, check if ALL required sub-fields have values
            const complexFieldNames = getComplexFieldNames(question)

            for (const fieldName of complexFieldNames) {
              const flatKey = `${question.slug}__${fieldName}`
              const value = currentFormData[flatKey]
              console.log(`  🔍 Complex field ${flatKey}:`, value)
              if (!value || (typeof value === 'string' && !value.trim())) {
                console.log(`  ❌ Required complex sub-field ${flatKey} is empty`)
                return false
              }
            }
          } else {
            // For simple fields
            const value = currentFormData[question.slug]
            console.log(`  🔍 Simple field ${question.slug}:`, value)
            if (!value || (typeof value === 'string' && !value.trim())) {
              console.log(`  ❌ Required simple field ${question.slug} is empty`)
              return false
            }
          }
        }
      }

      console.log('  ✅ All required fields are valid')
      return true
    })

    const loadQuestionTypes = async () => {
      try {
        console.log('📊 Loading question types...')
        const response = await questionTypesApi.getQuestionTypes()

        // Convert array to object keyed by slug for easy lookup
        const typesMap = {}
        response.data.forEach(type => {
          typesMap[type.slug] = type
        })
        questionTypes.value = typesMap

        console.log('📊 Question types loaded:', Object.keys(typesMap).join(', '))
      } catch (err) {
        console.error('Error loading question types:', err)
        error.value = 'Failed to load question types'
      }
    }

    const initializeCompletedPages = () => {
      if (!form.value?.pages) return

      const newCompletedPages = new Set()

      // Check each page to see if all required questions are answered
      form.value.pages.forEach((page, pageIndex) => {
        if (isPageComplete(pageIndex)) {
          newCompletedPages.add(pageIndex)
          console.log(`✅ Page ${pageIndex + 1} (${page.name}) is complete`)
        } else {
          console.log(`❌ Page ${pageIndex + 1} (${page.name}) is incomplete`)
        }
      })

      completedPages.value = newCompletedPages
      console.log('🏁 Initialized completed pages:', Array.from(newCompletedPages).map(i => i + 1))
    }

    const loadForm = async () => {
      // Prevent multiple simultaneous loads
      if (isLoadingForm.value) {
        console.log('🚫 Load already in progress, skipping')
        return
      }

      try {
        isLoadingForm.value = true
        loading.value = true
        error.value = null
        console.log('📥 Loading form:', props.formSlug)
        console.log('🔍 Current route params:', route.params)
        console.log('🔍 Looking for submissionId:', route.params.submissionId)

        let existingSubmission = null

        // First, check if we're loading a specific submission from URL
        if (route.params.submissionId) {
          console.log('📥 Loading specific submission from URL:', route.params.submissionId)
          try {
            const response = await submissionApi.getSubmission(route.params.submissionId)
            existingSubmission = response.data
            console.log('✅ Loaded submission:', existingSubmission.id)
          } catch (err) {
            console.error('❌ Error loading submission:', err)
            error.value = 'Submission not found or access denied'
            loading.value = false
            return
          }
        }

        // Load question types and form in parallel
        // If we have a submission, use its specific form version; otherwise use latest published
        await Promise.all([
          loadQuestionTypes(),
          (async () => {
            let response
            if (existingSubmission && existingSubmission.form_version_number) {
              console.log('📋 Loading form version', existingSubmission.form_version_number, 'for submission')
              response = await formApi.getFormVersion(props.formSlug, existingSubmission.form_version_number)
            } else {
              console.log('📋 Loading latest published form version')
              response = await formApi.getForm(props.formSlug)
            }
            form.value = response.data
            console.log('📋 Form structure loaded, pages:', form.value.pages?.length || 'N/A')
            // Emit form loaded event for parent components
            emit('form-loaded', form.value)
          })()
        ])

        // If no existing submission from URL, create a new one and redirect
        if (!existingSubmission) {
          console.log('🆕 No submission ID in URL, creating new submission')
          
          // Create new submission
          const submissionResponse = await submissionApi.createSubmission({
            form_slug: props.formSlug
          })
          existingSubmission = submissionResponse.data
          console.log('✅ Created new submission:', existingSubmission.id)

          // Immediately redirect to URL with submission ID
          const currentPageSlug = route.params.pageSlug
          const redirectRoute = currentPageSlug 
            ? { name: 'form-page', params: { slug: props.formSlug, submissionId: existingSubmission.id, pageSlug: currentPageSlug }}
            : { name: 'form-submission', params: { slug: props.formSlug, submissionId: existingSubmission.id }}
          
          console.log('🔄 Redirecting to submission-specific URL:', redirectRoute)
          router.replace(redirectRoute)
          return
        }

        submissionId.value = existingSubmission.id
        isComplete.value = existingSubmission.is_complete || false
        completedDateTime.value = existingSubmission.completed_datetime || null

        console.log('📊 Submission status:', isComplete.value ? 'Completed' : 'In Progress')
        if (completedDateTime.value) {
          console.log('✅ Completed at:', completedDateTime.value)
        }

        // Initialize form data with ALL saved answers or defaults
        // This creates the complete data structure for the entire form
        const initialData = {}

        // First, add all flat field data from saved submission
        if (existingSubmission.answers) {
          console.log('📄 Loading existing submission answers:', existingSubmission.answers)
          Object.entries(existingSubmission.answers).forEach(([key, value]) => {
            initialData[key] = value
            console.log(`  📝 Loaded: ${key} = "${value}"`)
          })
        } else {
          console.log('📄 No existing answers found in submission')
        }

        form.value.pages.forEach(page => {
          // Process individual questions
          if (page.questions) {
            page.questions.forEach(question => {
              initializeQuestionData(question, initialData)
            })
          }
          
          // Process questions from question groups
          if (page.question_groups) {
            page.question_groups.forEach(group => {
              if (group.questions) {
                group.questions.forEach(question => {
                  initializeQuestionData(question, initialData)
                })
              }
            })
          }
        })

        // Set the form data - FormKit will handle the binding
        formData.value = initialData

        // Initialize completed pages based on form data
        console.log('🎯 About to initialize completed pages with form data:', formData.value)
        initializeCompletedPages()

        // Initialize current page from URL or default to first page
        const initialPageIndex = getCurrentPageFromRoute()
        if (canNavigateToPage(initialPageIndex)) {
          currentPage.value = initialPageIndex
        } else {
          currentPage.value = 0
          // Navigate to first page if URL has invalid page
          if (route.params.pageSlug) {
            navigateToPage(0, true)
          }
        }

        // If no page slug in URL, navigate to first page
        if (!route.params.pageSlug && form.value.pages.length > 1) {
          navigateToPage(0, true)
        }

        console.log('🎯 Complete form data initialized:', Object.keys(initialData))
        console.log('🎯 FormData values:', formData.value)
        console.log('🎯 Individual values:')
        Object.entries(initialData).forEach(([key, value]) => {
          console.log(`  ${key}:`, JSON.stringify(value))
        })

        // If we just created a new submission and we're not already on the submission URL,
        // update the URL to reflect the submission-specific URL
        if (submissionId.value && !route.params.submissionId) {
          console.log('🔄 Updating URL to submission-specific URL:', submissionId.value)
          isUpdatingUrl.value = true

          // Determine if we need to include page slug
          const currentPageSlug = form.value.pages[currentPage.value]?.slug
          const hasMultiplePages = form.value.pages.length > 1

          // Use nextTick to ensure the router update happens after current cycle
          nextTick(() => {
            let routeConfig

            if (hasMultiplePages && currentPageSlug) {
              // Multi-page form with page slug
              routeConfig = {
                name: 'form-submission-page',
                params: {
                  slug: props.formSlug,
                  submissionId: submissionId.value,
                  pageSlug: currentPageSlug
                }
              }
            } else {
              // Single page form or no page slug
              routeConfig = {
                name: 'form-submission',
                params: {
                  slug: props.formSlug,
                  submissionId: submissionId.value
                }
              }
            }

            router.replace(routeConfig).then(() => {
              // Reset flag after navigation completes
              setTimeout(() => {
                isUpdatingUrl.value = false
                console.log('🔄 URL update completed, flag reset')
              }, 100)
            }).catch(() => {
              // Reset flag even if navigation fails
              isUpdatingUrl.value = false
              console.log('🔄 URL update failed, flag reset')
            })
          })
        }

      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to load form'
        console.error('Error loading form:', err)
      } finally {
        loading.value = false
        isLoadingForm.value = false
        // Allow normal field updates after initialization is complete
        setTimeout(() => {
          isInitializing.value = false
          console.log('🎯 Initialization complete, field updates now enabled')
        }, 100)
      }
    }

    const handleSubmit = async (data) => {
      try {
        submitting.value = true

        // Filter out complex nested objects and only submit flat fields
        const flatData = {}
        Object.entries(data).forEach(([key, value]) => {
          // Skip nested complex objects (they'll be submitted as flat fields)
          const question = findQuestionBySlug(key)
          if (question && isComplexQuestionType(question)) {
            console.log(`🏠 Skipping complex object ${key} in final submission, using flat fields`)
            return
          }

          // Include all flat fields and simple fields
          flatData[key] = value
        })

        console.log('🚀 Final submission flat data:', flatData)
        const response = await submissionApi.submitForm(submissionId.value, flatData)
        
        // Update local state to reflect completion
        isComplete.value = true
        completedDateTime.value = response.data.completed_datetime
        submitted.value = true
        
        // Navigate to submissions list after successful submission
        router.push({ 
          name: 'submissions', 
          params: { slug: props.formSlug } 
        })

      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to submit form'
        console.error('Error submitting form:', err)
      } finally {
        submitting.value = false
      }
    }

    // Auto-save form data to backend
    const saveFormData = async (data) => {
      if (!submissionId.value || !data) return

      try {
        // Filter out complex nested objects and only send flat fields
        const flatData = {}
        Object.entries(data).forEach(([key, value]) => {
          // Skip nested complex objects (they'll be saved as flat fields)
          const question = findQuestionBySlug(key)
          if (question && isComplexQuestionType(question)) {
            console.log(`🏠 Skipping complex object ${key}, will use flat fields instead`)
            return
          }

          // Include all flat fields and simple fields
          flatData[key] = value
        })

        console.log('📤 Saving flat data:', flatData)
        await submissionApi.updateSubmission(submissionId.value, {
          answers: flatData,
          is_complete: false
        })
        console.log('Form data auto-saved')
      } catch (err) {
        console.error('Error auto-saving form data:', err)
      }
    }


    // Debounced save function (saves 1 second after user stops typing)
    const debouncedSave = debounce(saveFormData, 1000)

    // Watch for form data changes and auto-save
    watch(
      () => formData.value,
      (newData, oldData) => {
        if (submissionId.value && newData && !isComplete.value) {
          debouncedSave(newData)
          // Recalculate page completion when form data changes
          if (!isInitializing.value) {
            console.log('🔄 Form data changed, recalculating page completion...')
            recalculatePageCompletion()
            
            // Handle conditional logic value clearing
            handleConditionalLogicValueClearing(newData, oldData)
          }
        }
      },
      { deep: true }
    )
    
    // Handle clearing values based on conditional logic
    const handleConditionalLogicValueClearing = (newData, oldData) => {
      if (!form.value?.pages || isInitializing.value) return
      
      const updatedFormData = { ...newData }
      let hasChanges = false
      
      form.value.pages.forEach(page => {
        // Check individual questions
        if (page.questions) {
          page.questions.forEach(question => {
            const logic = evaluateConditionalLogic(question, newData)
            if (!logic.visible && newData[question.slug] !== undefined && newData[question.slug] !== '') {
              console.log(`🧽 Clearing field ${question.slug} due to conditional logic`)
              updatedFormData[question.slug] = ''
              hasChanges = true
            }
          })
        }
        
        // Check questions in groups
        if (page.question_groups) {
          page.question_groups.forEach(group => {
            if (group.questions) {
              group.questions.forEach(question => {
                const logic = evaluateConditionalLogic(question, newData)
                if (!logic.visible && newData[question.slug] !== undefined && newData[question.slug] !== '') {
                  console.log(`🧽 Clearing field ${question.slug} due to conditional logic`)
                  updatedFormData[question.slug] = ''
                  hasChanges = true
                }
                
                // Also check flat field values for complex fields
                if (isComplexQuestionType(question) && !logic.visible) {
                  const complexFieldNames = getComplexFieldNames(question)
                  complexFieldNames.forEach(fieldName => {
                    const flatKey = `${question.slug}__${fieldName}`
                    if (newData[flatKey] !== undefined && newData[flatKey] !== '') {
                      console.log(`🧽 Clearing complex field ${flatKey} due to conditional logic`)
                      updatedFormData[flatKey] = ''
                      hasChanges = true
                    }
                  })
                }
              })
            }
          })
        }
      })
      
      if (hasChanges) {
        formData.value = updatedFormData
      }
    }

    const validateCurrentPage = () => {
      if (!currentPageData.value) return []
      const errors = []
      
      const allQuestions = visibleQuestions(currentPageData.value)
      for (const question of allQuestions) {
        if (question.required) {
          if (isComplexQuestionType(question)) {
            // For complex fields like address, check all required sub-fields
            const complexFieldNames = getComplexFieldNames(question)

            for (const fieldName of complexFieldNames) {
              const flatKey = `${question.slug}__${fieldName}`
              const value = formData.value[flatKey]
              if (!value || (typeof value === 'string' && !value.trim())) {
                const fieldLabel = fieldName.charAt(0).toUpperCase() + fieldName.slice(1).replace('_', ' ')
                errors.push(`${fieldLabel} is required`)
              }
            }
          } else {
            // For simple fields
            const value = formData.value[question.slug]
            if (!value || (typeof value === 'string' && !value.trim())) {
              errors.push(`${question.text || question.slug} is required`)
            }
          }
        }
      }

      return errors
    }

    const nextPage = () => {
      // Double-check validation (button should be disabled if invalid, but just in case)
      if (!isCurrentPageValid.value) {
        const validationErrors = validateCurrentPage()
        alert('Please complete all required fields:\n' + validationErrors.join('\n'))
        return
      }

      // Mark current page as completed
      completedPages.value.add(currentPage.value)

      if (currentPage.value < form.value.pages.length - 1) {
        const nextPageIndex = currentPage.value + 1
        navigateToPage(nextPageIndex)
        console.log('Navigated to page:', nextPageIndex + 1)
      }
    }

    const previousPage = () => {
      if (currentPage.value > 0) {
        const prevPageIndex = currentPage.value - 1
        navigateToPage(prevPageIndex)
        console.log('Navigated to page:', prevPageIndex + 1)
      }
    }

    const visibleQuestions = (page) => {
      const questions = []
      
      // Add individual questions
      if (page.questions) {
        questions.push(...page.questions.filter(question => {
          // Filter out hidden fields
          if (question.type === 'hidden' || question.config?.ui_hidden || question.config?.excluded_from_display) {
            return false
          }
          const logic = evaluateConditionalLogic(question, formData.value)
          return logic.visible
        }))
      }
      
      // Add questions from question groups
      if (page.question_groups) {
        page.question_groups.forEach(group => {
          if (group.questions) {
            questions.push(...group.questions.filter(question => {
              // Filter out hidden fields
              if (question.type === 'hidden' || question.config?.ui_hidden || question.config?.excluded_from_display) {
                return false
              }
              const logic = evaluateConditionalLogic(question, formData.value)
              return logic.visible
            }))
          }
        })
      }
      
      return questions
    }

    const getTableViewUrl = () => {
      if (submissionId.value) {
        return {
          name: 'form-submission-table',
          params: {
            slug: route.params.slug,
            submissionId: submissionId.value
          }
        }
      } else {
        return { name: 'form-table-editor', params: { slug: route.params.slug } }
      }
    }

    const getFormKitType = (question) => {
      // Get the question type from our loaded types
      const questionType = questionTypes.value[question.type]

      if (!questionType) {
        console.warn(`⚠️  Question type "${question.type}" not found in loaded types`)
        return 'text'
      }

      // Use the actual input_type from the question type config
      const inputType = questionType.config?.input_type

      if (inputType) {
        // Map Django input types to FormKit types
        const inputTypeMap = {
          'text': 'text',
          'email': 'email',
          'number': 'number',
          'textarea': 'textarea',
          'select': 'select',
          'radio': 'radio',
          'checkbox': 'checkbox',
          'date': 'date',
          'tel': 'tel',
          'url': 'url'
          // Note: 'address' is handled by custom AddressInput component, not FormKit
        }

        const formKitType = inputTypeMap[inputType]
        if (formKitType) {
          console.log(`📝 Question "${question.slug}" (${question.type}) using input_type "${inputType}" → FormKit "${formKitType}"`)
          return formKitType
        }
      }

      // Fallback to slug-based mapping for backwards compatibility
      const slugTypeMap = {
        'short-text': 'text',
        'text': 'text',
        'email': 'email',
        'number': 'number',
        'textarea': 'textarea',
        'select': 'select',
        'dropdown': 'select',
        'checkbox': 'checkbox',
        'radio': 'radio',
        'yes-no': 'radio',
        'date': 'date',
        'tel': 'tel',
        'url': 'url',
        'address': 'text'
      }

      const fallbackType = slugTypeMap[question.type] || 'text'
      console.log(`⚠️  Question "${question.slug}" (${question.type}) falling back to slug mapping → FormKit "${fallbackType}"`)
      return fallbackType
    }

    const getValidationRules = (question) => {
      const rules = []
      
      // Check conditional logic for dynamic required state
      const conditionalLogic = evaluateConditionalLogic(question, formData.value)
      if (conditionalLogic.required) {
        rules.push('required')
      }

      if (question.validation?.email) {
        rules.push('email')
      }

      if (question.validation?.min_length) {
        rules.push(`length:${question.validation.min_length}`)
      }

      if (question.validation?.max_length) {
        rules.push(`length:0,${question.validation.max_length}`)
      }

      return rules.join('|')
    }
    
    const getQuestionRequired = (question) => {
      const conditionalLogic = evaluateConditionalLogic(question, formData.value)
      return conditionalLogic.required
    }

    const getQuestionPlaceholder = (question) => {
      // Get the question type from our loaded types
      const questionType = questionTypes.value[question.type]

      if (!questionType) {
        console.warn(`⚠️  Question type "${question.type}" not found for placeholder`)
        return null
      }

      // Priority: question config > type config > fallback
      const questionPlaceholder = question.config?.placeholder
      const typePlaceholder = questionType.config?.placeholder

      if (typeof questionPlaceholder === 'string') {
        return questionPlaceholder
      }

      if (typeof questionPlaceholder === 'object' && questionPlaceholder?.en) {
        return questionPlaceholder.en
      }

      if (typeof typePlaceholder === 'string') {
        return typePlaceholder
      }

      if (typeof typePlaceholder === 'object' && typePlaceholder?.en) {
        return typePlaceholder.en
      }

      return null
    }

    const getQuestionOptions = (question) => {
      // First check if conditional logic provides dynamic options
      const conditionalLogic = evaluateConditionalLogic(question, formData.value)
      if (conditionalLogic.options) {
        console.log(`🎯 Using conditional logic options for ${question.slug}:`, conditionalLogic.options)
        return conditionalLogic.options
      }
      
      // Get the question type from our loaded types
      const questionType = questionTypes.value[question.type]

      if (!questionType) {
        console.warn(`⚠️  Question type "${question.type}" not found for options`)
        return []
      }

      // Handle different option formats from Django
      const questionConfig = question.config
      const typeConfig = questionType.config

      console.log(`🎯 Getting options for ${question.slug} (${question.type})`)
      console.log('  Question config:', questionConfig)
      console.log('  Type config:', typeConfig)

      // Priority order: question config options > type config options > defaults
      let options = null

      // 1. Check question-specific options first
      if (questionConfig?.options) {
        options = questionConfig.options
        console.log('  → Using question-specific options')
      }
      // 2. Check question type default options
      else if (typeConfig?.options) {
        options = typeConfig.options
        console.log('  → Using question type default options')
      }

      if (options) {
        // Use English options by default, fallback to first available language
        const finalOptions = options.en || options[Object.keys(options)[0]] || []
        console.log('  → Final options:', finalOptions)
        return finalOptions
      }

      // 3. Handle special cases like yes/no
      if (question.type === 'yes-no') {
        const defaultYesNo = [
          { label: 'Yes', value: 'yes' },
          { label: 'No', value: 'no' }
        ]
        console.log('  → Using default yes/no options')
        return defaultYesNo
      }

      console.log('  → No options found, returning empty array')
      return []
    }

    const getQuestionTypeConfig = (question) => {
      // Get the question type from our loaded types
      const questionType = questionTypes.value[question.type]
      return questionType?.config || {}
    }

    const getFormattedLabel = (question) => {
      if (question.required) {
        return `${question.text} <span style="color: #ef4444; font-weight: normal;">*</span>`
      }
      return question.text
    }

    const isRadioOrCheckbox = (question) => {
      // Detect radio buttons and checkboxes that need special label handling
      const formKitType = getFormKitType(question)
      return formKitType === 'radio' || formKitType === 'checkbox'
    }

    const isDisabledSelect = (question, page) => {
      const formKitType = getFormKitType(question)
      const isSelectType = formKitType === 'select'
      const isDisabled = isQuestionDisabled(question, page, formData.value) || isComplete.value
      return isSelectType && isDisabled
    }

    const updateField = (fieldName, value) => {
      console.log(`🔄 Updating ${fieldName}:`, value)

      // Ensure reactivity by creating a new object reference
      const newFormData = { ...formData.value }
      newFormData[fieldName] = value

      // Only do flattening if we're not initializing to prevent excessive updates
      if (!isInitializing.value) {
        // If this is a complex field (like address), also update the flat field storage
        const question = findQuestionBySlug(fieldName)
        if (question && isComplexQuestionType(question)) {
          console.log(`🏠 Flattening complex field ${fieldName}:`, value)
          const flatData = flattenComplexValue(fieldName, value)
          Object.entries(flatData).forEach(([flatKey, flatValue]) => {
            newFormData[flatKey] = flatValue
            console.log(`  📝 Set ${flatKey} = "${flatValue}"`)
          })
        }
      } else {
        console.log(`🎯 Skipping flattening during initialization for ${fieldName}`)
      }

      // Set the new form data object to trigger reactivity
      formData.value = newFormData
      console.log(`🔄 Updated formData, field ${fieldName} now:`, formData.value[fieldName])

      // Immediately recalculate page completion after field update
      if (!isInitializing.value) {
        console.log('🔄 Field updated, immediately recalculating page completion...')
        // Use nextTick to ensure the form data has been processed
        nextTick(() => {
          recalculatePageCompletion()
        })
      }
    }


    const initializeQuestionData = (question, initialData) => {
      if (isComplexQuestionType(question)) {
        // For complex types like address, initialize flat fields and create nested view
        const complexFieldNames = getComplexFieldNames(question)
        complexFieldNames.forEach(fieldName => {
          const flatKey = `${question.slug}__${fieldName}`
          if (!(flatKey in initialData)) {
            initialData[flatKey] = ''
          }
        })

        // Create nested object for form display
        const complexValue = unflattenComplexValue(question.slug, initialData)
        initialData[question.slug] = complexValue || {
          street: '',
          city: '',
          state: '',
          postal_code: '',
          country: ''
        }

        console.log(`🏠 Initialized complex field ${question.slug}:`, initialData[question.slug])
      } else {
        // Simple field handling
        if (!(question.slug in initialData)) {
          const defaultValue = question.config?.default_value || ''
          initialData[question.slug] = defaultValue
        }
      }
    }

    const findQuestionBySlug = (slug) => {
      for (const page of form.value?.pages || []) {
        // Check individual questions
        if (page.questions) {
          for (const question of page.questions) {
            if (question.slug === slug) {
              return question
            }
          }
        }
        
        // Check questions in groups
        if (page.question_groups) {
          for (const group of page.question_groups) {
            if (group.questions) {
              for (const question of group.questions) {
                if (question.slug === slug) {
                  return question
                }
              }
            }
          }
        }
      }
      return null
    }

    // Utility functions for handling complex question types (e.g., address)
    const isComplexQuestionType = (question) => {
      const questionType = questionTypes.value[question.type]
      return questionType?.config?.input_type === 'address'
    }

    const getComplexFieldNames = (question) => {
      const questionType = questionTypes.value[question.type]
      if (questionType?.config?.input_type === 'address') {
        return ['street', 'city', 'state', 'postal_code', 'country']
      }
      return []
    }

    const flattenComplexValue = (questionSlug, complexValue) => {
      const flatData = {}
      if (complexValue && typeof complexValue === 'object') {
        Object.entries(complexValue).forEach(([subField, value]) => {
          flatData[`${questionSlug}__${subField}`] = value || ''
        })
      }
      return flatData
    }

    const unflattenComplexValue = (questionSlug, flatData) => {
      const complexValue = {}
      const prefix = `${questionSlug}__`

      Object.entries(flatData).forEach(([key, value]) => {
        if (key.startsWith(prefix)) {
          const subField = key.substring(prefix.length)
          complexValue[subField] = value
        }
      })

      return Object.keys(complexValue).length > 0 ? complexValue : null
    }

    // Conditional Logic Evaluation System
    const evaluateCondition = (condition, formData) => {
      const { question_slug, operator, value } = condition
      const fieldValue = formData[question_slug]
      
      switch (operator) {
        case 'equals':
          return fieldValue === value
        case 'not_equals':
          return fieldValue !== value
        case 'contains':
          return fieldValue && fieldValue.toString().includes(value)
        case 'not_contains':
          return !fieldValue || !fieldValue.toString().includes(value)
        case 'is_empty':
          return !fieldValue || fieldValue === ''
        case 'is_not_empty':
          return fieldValue && fieldValue !== ''
        default:
          console.warn(`Unknown condition operator: ${operator}`)
          return false
      }
    }
    
    const evaluateRule = (rule, formData) => {
      const { conditions, logical_operator } = rule
      
      if (!conditions || conditions.length === 0) {
        return true
      }
      
      const results = conditions.map(condition => evaluateCondition(condition, formData))
      
      if (logical_operator === 'OR') {
        return results.some(result => result)
      } else {
        // Default to AND
        return results.every(result => result)
      }
    }
    
    const evaluateConditionalLogic = (question, formData) => {
      if (!question.conditional_logic || !question.conditional_logic.rules) {
        return {
          visible: true,
          required: question.required || false,
          options: null
        }
      }
      
      const { rules, default_action } = question.conditional_logic
      
      // Find the first matching rule
      for (const rule of rules) {
        if (evaluateRule(rule, formData)) {
          // Apply the actions from the matching rule
          let visible = true
          let required = question.required || false
          let options = null
          
          for (const action of rule.actions) {
            switch (action.type) {
              case 'show':
                visible = true
                break
              case 'hide':
                visible = false
                break
              case 'require':
                required = true
                break
              case 'unrequire':
                required = false
                break
              case 'set_options':
                options = action.options?.en || action.options
                break
              case 'clear_value':
                // This should be handled by the caller
                break
            }
          }
          
          return { visible, required, options }
        }
      }
      
      // No rules matched, apply default action
      if (default_action === 'hide') {
        return {
          visible: false,
          required: false,
          options: null
        }
      }
      
      // Default: show the question as configured
      return {
        visible: true,
        required: question.required || false,
        options: null
      }
    }

    const startNewSubmission = () => {
      // Clear the form state and reload
      submitted.value = false
      submissionId.value = null
      formData.value = {}
      currentPage.value = 0
      completedPages.value = new Set()

      // Reload form (will create new submission and redirect to new URL)
      loadForm()
    }

    // Watch route changes to update current page
    watch(
      () => route.params.pageSlug,
      (newPageSlug) => {
        if (form.value && newPageSlug) {
          const pageIndex = getCurrentPageFromRoute()
          if (canNavigateToPage(pageIndex)) {
            currentPage.value = pageIndex
          } else {
            // Redirect to first accessible page if trying to access restricted page
            console.log(`⚠️ Cannot navigate to page ${pageIndex + 1}, redirecting to first accessible page`)
            const firstAccessiblePage = findFirstAccessiblePage()
            if (firstAccessiblePage >= 0) {
              navigateToPage(firstAccessiblePage, true)
            }
          }
        } else if (form.value && !newPageSlug) {
          // If no page slug, navigate to first page
          navigateToPage(0, true)
        }
      }
    )

    // Watch for changes in page completion that might affect current page accessibility
    watch(
      () => completedPages.value,
      (_, oldCompletedPages) => {
        if (form.value && oldCompletedPages) {
          // Check if current page is still accessible
          if (!canNavigateToPage(currentPage.value)) {
            console.log(`⚠️ Current page ${currentPage.value + 1} is no longer accessible, redirecting`)
            const firstAccessiblePage = findFirstAccessiblePage()
            if (firstAccessiblePage >= 0 && firstAccessiblePage !== currentPage.value) {
              navigateToPage(firstAccessiblePage, true)
            }
          }
        }
      },
      { deep: true }
    )

    const findFirstAccessiblePage = () => {
      if (!form.value?.pages) return 0
      for (let i = 0; i < form.value.pages.length; i++) {
        if (canNavigateToPage(i)) return i
      }
      return 0
    }

    // Watch for route changes to handle navigation between form and submission URLs
    watch(
      () => route.params,
      (newParams, oldParams) => {
        console.log('🔄 Route params changed:', { old: oldParams, new: newParams })

        // Skip if we're programmatically updating the URL
        if (isUpdatingUrl.value) {
          console.log('🔄 Skipping reload - programmatic URL update')
          isUpdatingUrl.value = false
          return
        }

        // Only reload if the form slug changed
        // Don't reload when transitioning to/from a submissionId - this prevents infinite loops
        if (oldParams?.slug !== newParams?.slug) {
          console.log('🔄 Form slug changed, reloading form')
          loadForm()
        } else if (oldParams?.submissionId !== newParams?.submissionId) {
          console.log('🔄 SubmissionId changed but form slug same - skipping reload to prevent infinite loop')
          // Just update our local submissionId if needed
          if (newParams?.submissionId && newParams.submissionId !== submissionId.value) {
            submissionId.value = newParams.submissionId
            console.log('🔄 Updated local submissionId to match route:', submissionId.value)
          }
        }
      },
      { immediate: true } // Run immediately on mount
    )

    onMounted(() => {
      console.log('🔄 DynamicForm component mounted - formSlug:', props.formSlug)
      // loadForm() is now handled by the route watcher
    })

    onUnmounted(() => {
      console.log('❌ DynamicForm component unmounted - formSlug:', props.formSlug)
    })

    return {
      form,
      formData,
      loading,
      error,
      submitting,
      submitted,
      submissionId,
      currentPage,
      currentPageData,
      visiblePages,
      isLastPage,
      isFormReady,
      isCurrentPageValid,
      canNavigateToPage,
      navigateToPage,
      completedPages,
      isComplete,
      completedDateTime,
      handleSubmit,
      nextPage,
      previousPage,
      visibleQuestions,
      isComplexQuestionType,
      getFormKitType,
      getValidationRules,
      getQuestionPlaceholder,
      getQuestionOptions,
      getQuestionTypeConfig,
      getFormattedLabel,
      isRadioOrCheckbox,
      isDisabledSelect,
      updateField,
      getTableViewUrl,
      startNewSubmission
    }
  }
}
</script>

<style scoped>
</style>