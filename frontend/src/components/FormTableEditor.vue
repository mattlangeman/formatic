<template>
  <div class="form-table-editor">
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

    <div v-else-if="form && isFormReady">
      <div class="form-header mb-8">
        <!-- Navigation link to submissions -->
        <div class="mb-4">
          <router-link 
            :to="{ name: 'submissions', params: { slug: form.slug } }"
            class="inline-flex items-center text-sm text-primary-600 hover:text-primary-800 transition-colors"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Submissions
          </router-link>
        </div>
        
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ form.name }}</h1>
        <p v-if="form.description" class="text-gray-600">{{ form.description }}</p>
        
        <div class="mt-4 flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="text-sm text-gray-500">
              Table Editor - All pages on one screen
            </div>
            <span class="text-gray-400">|</span>
            <router-link 
              :to="getFormViewUrl()"
              class="text-sm text-primary-600 hover:text-primary-800 transition-colors"
            >
              Switch to Form View
            </router-link>
            <span class="text-gray-400">|</span>
            <div v-if="isComplete" class="inline-flex items-center text-sm">
              <svg class="w-4 h-4 mr-1 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span class="text-green-600 font-medium">Completed</span>
              <span v-if="completedDateTime" class="text-gray-500 ml-2">
                {{ new Date(completedDateTime).toLocaleString() }}
              </span>
            </div>
            <div v-else class="inline-flex items-center text-sm">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                In Progress
              </span>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <button
              v-if="!isComplete"
              @click="saveForm"
              :disabled="saving"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
            <button
              v-if="!isComplete"
              @click="completeForm"
              :disabled="saving || !allRequiredFieldsFilled"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              :title="!allRequiredFieldsFilled ? 'Please fill in all required fields' : 'Complete and submit the form'"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Complete Form
            </button>
            <button
              v-if="!isComplete"
              @click="resetForm"
              class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      <!-- Main Content Area: Form Tables + Charts -->
      <div class="flex gap-6">
        <!-- Left Side: Form Tables (50% width) -->
        <div class="w-1/2 space-y-8">
        <div 
          v-for="page in form.pages" 
          :key="page.id"
          class="bg-white shadow-sm rounded-lg overflow-hidden border border-gray-200"
        >
          <!-- Page Title Header -->
          <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900">{{ page.name }}</h2>
            <p v-if="page.description" class="text-sm text-gray-600 mt-1">{{ page.description }}</p>
          </div>

          <!-- Questions Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <tbody class="bg-white divide-y divide-gray-200">
                <template v-for="question in getAllQuestionsFromPage(page)" :key="question.id">
                  <!-- Address Question - Split into multiple rows -->
                  <template v-if="isAddressField(question)">
                    <!-- Main Address Question Row -->
                    <tr class="hover:bg-gray-50">
                      <td class="px-6 py-2 whitespace-normal text-sm text-gray-900 align-top border-r border-gray-100 w-1/3">
                        <div class="flex items-center relative">
                          <div class="font-medium" v-html="getFormattedLabel(question)"></div>
                          <div v-if="question.subtext" class="relative ml-1">
                            <svg 
                              @click="toggleTooltip(`address-${question.id}`)"
                              @mouseenter="showTooltip(`address-${question.id}`)"
                              @mouseleave="hideTooltip(`address-${question.id}`)"
                              class="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-pointer"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
                            </svg>
                            <div 
                              v-if="activeTooltip === `address-${question.id}`"
                              class="absolute left-0 top-6 z-50 w-64 p-3 text-xs text-white bg-gray-900 rounded-lg shadow-lg"
                            >
                              {{ question.subtext }}
                              <div class="absolute -top-1 left-2 w-2 h-2 bg-gray-900 rotate-45"></div>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="px-6 py-2 text-xs text-gray-500 italic w-2/3">
                        Address components below ↓
                      </td>
                    </tr>
                    
                    <!-- Street Address Row -->
                    <tr class="hover:bg-gray-50">
                      <td class="px-6 py-2 pl-12 text-sm text-gray-600 border-r border-gray-100">
                        <div class="flex items-center">
                          <span class="text-gray-400 mr-2">└</span>
                          Street Address
                          <span v-if="question.required" class="text-red-400 ml-1">*</span>
                        </div>
                      </td>
                      <td class="px-6 py-2">
                        <FormKit
                          type="text"
                          :name="`${question.slug}__street`"
                          :model-value="formData[`${question.slug}__street`]"
                          @update:model-value="(value) => updateField(`${question.slug}__street`, value)"
                          :validation="question.required ? 'required' : undefined"
                          placeholder="Enter street address"
                          :disabled="isFieldDisabled(question, page)"
                          outer-class="form-table-field"
                          wrapper-class="form-table-wrapper"
                          input-class="form-table-input"
                        />
                      </td>
                    </tr>

                    <!-- City Row -->
                    <tr class="hover:bg-gray-50">
                      <td class="px-6 py-2 pl-12 text-sm text-gray-600 border-r border-gray-100">
                        <div class="flex items-center">
                          <span class="text-gray-400 mr-2">└</span>
                          City
                          <span v-if="question.required" class="text-red-400 ml-1">*</span>
                        </div>
                      </td>
                      <td class="px-6 py-2">
                        <FormKit
                          type="text"
                          :name="`${question.slug}__city`"
                          :model-value="formData[`${question.slug}__city`]"
                          @update:model-value="(value) => updateField(`${question.slug}__city`, value)"
                          :validation="question.required ? 'required' : undefined"
                          placeholder="Enter city"
                          :disabled="isFieldDisabled(question, page)"
                          outer-class="form-table-field"
                          wrapper-class="form-table-wrapper"
                          input-class="form-table-input"
                        />
                      </td>
                    </tr>

                    <!-- State/Province Row with Conditional Logic -->
                    <tr v-if="getStateFieldVisibilityWrapper(question)" class="hover:bg-gray-50">
                      <td class="px-6 py-2 pl-12 text-sm text-gray-600 border-r border-gray-100">
                        <div class="flex items-center">
                          <span class="text-gray-400 mr-2">└</span>
                          State/Province
                          <span v-if="getStateFieldRequiredWrapper(question)" class="text-red-400 ml-1">*</span>
                        </div>
                      </td>
                      <td class="px-6 py-2">
                        <FormKit
                          :type="getStateFieldTypeWrapper(question)"
                          :name="`${question.slug}__state`"
                          :model-value="formData[`${question.slug}__state`]"
                          @update:model-value="(value) => updateField(`${question.slug}__state`, value)"
                          :validation="getStateFieldRequiredWrapper(question) ? 'required' : undefined"
                          :placeholder="getStateFieldPlaceholderWrapper(question)"
                          :options="getStateFieldOptionsWrapper(question)"
                          :disabled="isFieldDisabled(question, page)"
                          outer-class="form-table-field"
                          wrapper-class="form-table-wrapper"
                          input-class="form-table-input"
                        />
                      </td>
                    </tr>

                    <!-- Postal Code Row -->
                    <tr class="hover:bg-gray-50">
                      <td class="px-6 py-2 pl-12 text-sm text-gray-600 border-r border-gray-100">
                        <div class="flex items-center">
                          <span class="text-gray-400 mr-2">└</span>
                          Postal Code
                          <span v-if="question.required" class="text-red-400 ml-1">*</span>
                        </div>
                      </td>
                      <td class="px-6 py-2">
                        <FormKit
                          type="text"
                          :name="`${question.slug}__postal_code`"
                          :model-value="formData[`${question.slug}__postal_code`]"
                          @update:model-value="(value) => updateField(`${question.slug}__postal_code`, value)"
                          :validation="question.required ? 'required' : undefined"
                          placeholder="Enter postal code"
                          :disabled="isFieldDisabled(question, page)"
                          outer-class="form-table-field"
                          wrapper-class="form-table-wrapper"
                          input-class="form-table-input"
                        />
                      </td>
                    </tr>

                    <!-- Country Row -->
                    <tr class="hover:bg-gray-50 border-b-2 border-gray-200">
                      <td class="px-6 py-2 pl-12 text-sm text-gray-600 border-r border-gray-100">
                        <div class="flex items-center">
                          <span class="text-gray-400 mr-2">└</span>
                          Country
                          <span v-if="question.required" class="text-red-400 ml-1">*</span>
                        </div>
                      </td>
                      <td class="px-6 py-2">
                        <FormKit
                          type="select"
                          :name="`${question.slug}__country`"
                          :model-value="formData[`${question.slug}__country`]"
                          @update:model-value="(value) => updateField(`${question.slug}__country`, value)"
                          :validation="question.required ? 'required' : undefined"
                          :options="getCountryOptions(question)"
                          placeholder="Select a country"
                          :disabled="isFieldDisabled(question, page)"
                          outer-class="form-table-field"
                          wrapper-class="form-table-wrapper"
                          input-class="form-table-input"
                        />
                      </td>
                    </tr>
                  </template>

                  <!-- Regular Questions -->
                  <tr v-else class="hover:bg-gray-50" :key="`regular-${question.id}`">
                    <!-- Question Column -->
                    <td class="px-6 py-2 whitespace-normal text-sm text-gray-900 border-r border-gray-100 w-1/3" :class="isSingleLineInput(question) ? 'align-middle' : 'align-top'">
                      <div class="flex items-center relative">
                        <div class="font-medium" v-html="getFormattedLabel(question)"></div>
                        <div v-if="question.subtext" class="relative ml-1">
                          <svg 
                            @click="toggleTooltip(`regular-${question.id}`)"
                            @mouseenter="showTooltip(`regular-${question.id}`)"
                            @mouseleave="hideTooltip(`regular-${question.id}`)"
                            class="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-pointer"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
                          </svg>
                          <div 
                            v-if="activeTooltip === `regular-${question.id}`"
                            class="absolute left-0 top-6 z-50 w-64 p-3 text-xs text-white bg-gray-900 rounded-lg shadow-lg"
                          >
                            {{ question.subtext }}
                            <div class="absolute -top-1 left-2 w-2 h-2 bg-gray-900 rotate-45"></div>
                          </div>
                        </div>
                      </div>
                    </td>

                    <!-- Answer Column -->
                    <td class="px-6 py-2 text-sm text-gray-900 w-2/3" :class="isSingleLineInput(question) ? 'align-middle' : 'align-top'">
                      <div :class="isRadioOrCheckbox(question) ? 'radio-checkbox-field' : 'max-w-lg'">
                        <FormKit
                          :type="getFormKitType(question)"
                          :name="question.slug"
                          :model-value="formData[question.slug]"
                          @update:model-value="(value) => updateField(question.slug, value)"
                          :validation="getValidationRules(question)"
                          :placeholder="getQuestionPlaceholder(question)"
                          :options="getQuestionOptions(question)"
                          :multiple="question.config?.multiple"
                          :required="question.required"
                          :disabled="isFieldDisabled(question, page)"
                          outer-class="form-table-field"
                          wrapper-class="form-table-wrapper"
                          input-class="form-table-input"
                        />
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>

        </div>

        <!-- Right Side: Charts & Analytics (50% width) -->
        <div class="w-1/2">
          <div class="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-6">Form Analytics</h2>
            
            <!-- Chart Placeholders -->
            <div class="space-y-6">
              <!-- Completion Progress Chart -->
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <div class="mb-4">
                  <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Completion Progress</h3>
                <p class="text-gray-500 text-sm">Chart showing form completion progress over time</p>
              </div>

              <!-- Field Completion Status -->
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <div class="mb-4">
                  <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Field Completion</h3>
                <p class="text-gray-500 text-sm">Pie chart showing completed vs incomplete fields</p>
              </div>

              <!-- Response Summary -->
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <div class="mb-4">
                  <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Response Analysis</h3>
                <p class="text-gray-500 text-sm">Summary statistics and response patterns</p>
              </div>

              <!-- Time Analytics -->
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <div class="mb-4">
                  <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Time Analytics</h3>
                <p class="text-gray-500 text-sm">Time spent on form and completion rates</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="form" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Preparing form...</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { formApi, submissionApi, questionTypesApi } from '../services/api'
import { useConditionalLogic } from '../composables/useConditionalLogic.js'
import { useAddressField } from '../composables/useAddressField.js'

export default {
  name: 'FormTableEditor',
  setup(props, { emit }) {
    const route = useRoute()
    
    // Use shared composables
    const { getVisibleQuestions, evaluateConditionalLogic, getQuestionOptions: getConditionalQuestionOptions, isPageDisabled, isQuestionDisabled } = useConditionalLogic()
    const {
      getStateFieldVisibility,
      getStateFieldRequired,
      getStateFieldType,
      getStateFieldOptions,
      getStateFieldPlaceholder
    } = useAddressField()
    
    // State
    const form = ref(null)
    const formData = ref({})
    const questionTypes = ref({})
    const loading = ref(true)
    const error = ref(null)
    const saving = ref(false)
    const submissionId = ref(null)
    const originalFormData = ref({})
    const isComplete = ref(false)
    const completedDateTime = ref(null)
    const activeTooltip = ref(null)

    // Computed properties
    const isFormReady = computed(() => {
      return form.value && Object.keys(formData.value).length > 0 && Object.keys(questionTypes.value).length > 0
    })


    const allRequiredFieldsFilled = computed(() => {
      if (!form.value || !formData.value) return false
      
      let allFilled = true
      
      const checkQuestion = (question) => {
        if (!question.required) return // Skip non-required fields
        
        if (isAddressField(question)) {
          // For address fields, check all required sub-fields
          const addressFields = ['street', 'city', 'state', 'postal_code', 'country']
          for (const field of addressFields) {
            const value = formData.value[`${question.slug}__${field}`]
            if (value === undefined || value === null || value === '' || 
                (typeof value === 'string' && value.trim() === '')) {
              console.log(`❌ Required address field missing: ${question.slug}__${field}`)
              allFilled = false
            }
          }
        } else {
          // Regular field
          const value = formData.value[question.slug]
          if (value === undefined || value === null || value === '' || 
              (Array.isArray(value) && value.length === 0) ||
              (typeof value === 'string' && value.trim() === '')) {
            console.log(`❌ Required field missing: ${question.slug}`)
            allFilled = false
          }
        }
      }
      
      form.value.pages.forEach(page => {
        // Check individual questions
        if (page.questions) {
          page.questions.forEach(checkQuestion)
        }
        
        // Check questions from question groups
        if (page.question_groups) {
          page.question_groups.forEach(group => {
            if (group.questions) {
              group.questions.forEach(checkQuestion)
            }
          })
        }
      })
      
      return allFilled
    })

    // Helper function to get all questions from a page (including group questions)
    const getAllQuestionsFromPage = (page) => {
      return getVisibleQuestions(page, formData.value)
    }
    
    // State field conditional logic helpers (using shared composable) - made reactive
    const getStateFieldVisibilityWrapper = computed(() => {
      return (addressQuestion) => {
        const transformedData = {
          address_country: formData.value['address_country']
        }
        const result = getStateFieldVisibility(form.value, transformedData)
        console.log('🔍 State field visibility:', result)
        return result
      }
    })
    
    const getStateFieldRequiredWrapper = computed(() => {
      return (addressQuestion) => {
        const transformedData = {
          address_country: formData.value['address_country']
        }
        const result = getStateFieldRequired(form.value, transformedData)
        console.log('🔍 State field required:', result)
        return result
      }
    })
    
    const getStateFieldTypeWrapper = computed(() => {
      return (addressQuestion) => {
        const transformedData = {
          address_country: formData.value['address_country']
        }
        const result = getStateFieldType(form.value, transformedData)
        console.log('🔍 State field type:', result)
        return result
      }
    })
    
    const getStateFieldOptionsWrapper = computed(() => {
      return (addressQuestion) => {
        // In this form structure, address fields are individual questions with slugs like 'address_country'
        // The actual country value is stored directly as 'address_country', not flattened
        const transformedData = {
          address_country: formData.value['address_country']
        }
        
        const result = getStateFieldOptions(form.value, transformedData)
        console.log('🔍 State field options:', result?.length || 0, 'options found')
        console.log('🔍 Country value:', transformedData.address_country)
        console.log('🔍 All formData keys:', Object.keys(formData.value))
        return result
      }
    })
    
    const getStateFieldPlaceholderWrapper = computed(() => {
      return (addressQuestion) => {
        const transformedData = {
          address_country: formData.value['address_country']
        }
        const result = getStateFieldPlaceholder(form.value, transformedData)
        console.log('🔍 State field placeholder:', result)
        return result
      }
    })

    // Utility functions (copied from DynamicForm.vue)
    const getCsrfToken = () => {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1]
      
      if (!token) {
        console.warn('CSRF token not found in cookies')
      }
      
      return token
    }

    const getFormKitType = (question) => {
      // Get the question type from our loaded types
      const questionType = questionTypes.value[question.type]
      
      if (!questionType) {
        console.warn(`⚠️  Question type "${question.type}" not found in loaded types`)
        // Fallback to slug-based mapping when question type not found
        const slugTypeMap = {
          'short-text': 'text',
          'long-text': 'textarea',
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
        
        return inputTypeMap[inputType] || 'text'
      }
      
      // Secondary fallback with slug-based mapping
      const slugTypeMap = {
        'short-text': 'text',
        'long-text': 'textarea',
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
      
      if (question.required) {
        rules.push('required')
      }
      
      const questionType = questionTypes.value[question.type]
      if (questionType?.config?.input_type === 'email') {
        rules.push('email')
      }
      
      return rules.join('|') || undefined
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
      return questionTypes.value[question.type]?.config || {}
    }

    const getFormattedLabel = (question) => {
      if (question.required) {
        return `${question.text} <span style="color: #ef4444; font-weight: normal;">*</span>`
      }
      return question.text || question.slug
    }


    const isAddressField = (question) => {
      const questionType = questionTypes.value[question.type]
      const isAddress = questionType?.config?.input_type === 'address'
      
      if (question.slug && question.slug.includes('address')) {
        console.log(`🔍 Checking if ${question.slug} is address field:`)
        console.log(`  question.type: ${question.type}`)
        console.log(`  questionType found: ${!!questionType}`)
        console.log(`  input_type: ${questionType?.config?.input_type}`)
        console.log(`  isAddress: ${isAddress}`)
      }
      
      return isAddress
    }

    const isComplexQuestionType = (question) => {
      return isAddressField(question)
    }

    const isRadioOrCheckbox = (question) => {
      const formKitType = getFormKitType(question)
      return formKitType === 'radio' || formKitType === 'checkbox'
    }

    const isSingleLineInput = (question) => {
      const formKitType = getFormKitType(question)
      // Single-line inputs that should be center-aligned
      const singleLineTypes = ['text', 'email', 'number', 'tel', 'url', 'password', 'date', 'time', 'datetime-local', 'month', 'week', 'select', 'radio']
      return singleLineTypes.includes(formKitType)
    }

    const getCountryOptions = (question) => {
      // Get the address question type configuration
      const questionType = questionTypes.value[question.type]
      
      if (!questionType?.config?.country_options) {
        console.warn('⚠️ No country options found for address field')
        // Fallback to basic country list
        return [
          { label: 'United States', value: 'US' },
          { label: 'Canada', value: 'CA' },
          { label: 'United Kingdom', value: 'GB' },
          { label: 'France', value: 'FR' },
          { label: 'Germany', value: 'DE' },
          { label: 'Spain', value: 'ES' }
        ]
      }
      
      // Get language-specific options (default to English)
      const countryOptions = questionType.config.country_options
      const options = countryOptions.en || countryOptions[Object.keys(countryOptions)[0]] || []
      
      console.log('🌍 Country options loaded:', options.length, 'countries')
      return options
    }

    const updateField = (fieldName, value) => {
      console.log(`🔄 Table Editor - Updating ${fieldName}:`, value)
      
      const newFormData = { ...formData.value }
      newFormData[fieldName] = value
      formData.value = newFormData
      
      console.log(`🔄 Updated formData, field ${fieldName} now:`, formData.value[fieldName])
    }

    // Helper function to determine if a field should be disabled
    const isFieldDisabled = (question, page) => {
      // Always disabled if form is complete
      if (isComplete.value) {
        return true
      }
      
      // Check if question is disabled by page or question conditions
      const disabled = isQuestionDisabled(question, page, formData.value)
      
      // Debug logging for page-4 (Project Demands)
      if (page.slug === 'page-4') {
        console.log(`🔒 Field ${question.slug} disabled check:`, {
          pageSlug: page.slug,
          disabled_condition: page.disabled_condition,
          tool_mode: formData.value.tool_mode,
          disabled
        })
      }
      
      return disabled
    }

    // Helper to find page for a question
    const findPageForQuestion = (questionToFind) => {
      if (!form.value?.pages) return null
      
      for (const page of form.value.pages) {
        // Check regular questions
        if (page.questions?.some(q => q.id === questionToFind.id)) {
          return page
        }
        
        // Check questions in groups
        if (page.question_groups) {
          for (const group of page.question_groups) {
            if (group.questions?.some(q => q.id === questionToFind.id)) {
              return page
            }
          }
        }
      }
      return null
    }

    const getFormViewUrl = () => {
      if (submissionId.value) {
        return { 
          name: 'form-submission', 
          params: { 
            slug: route.params.slug, 
            submissionId: submissionId.value 
          }
        }
      } else {
        return { name: 'form', params: { slug: route.params.slug } }
      }
    }

    // API functions
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
        console.error('❌ Error loading question types:', err)
        throw err
      }
    }

    const loadForm = async (slug) => {
      try {
        console.log('📥 Loading form:', slug)
        const response = await formApi.getForm(slug)
        form.value = response.data
        
        console.log('✅ Form loaded:', response.data.name)
        console.log('📄 Pages:', response.data.pages.length)
        
        // Emit form loaded event for parent components
        emit('form-loaded', response.data)
        
        return response.data
      } catch (err) {
        console.error('❌ Error loading form:', err)
        throw err
      }
    }

    const loadSubmissionById = async (submissionIdParam) => {
      try {
        console.log('📥 Loading submission by ID:', submissionIdParam)
        
        const response = await submissionApi.getSubmission(submissionIdParam)
        const submission = response.data
        
        console.log('📄 Loaded submission:', submission)
        
        submissionId.value = submission.id
        isComplete.value = submission.is_complete || false
        completedDateTime.value = submission.completed_datetime || null
        
        console.log('📊 Submission status:', isComplete.value ? 'Completed' : 'In Progress')
        if (completedDateTime.value) {
          console.log('✅ Completed at:', completedDateTime.value)
        }
        
        return submission.answers || {}
      } catch (err) {
        console.error('❌ Error loading submission:', err)
        throw err
      }
    }

    const saveForm = async () => {
      if (!submissionId.value) return
      
      saving.value = true
      try {
        await submissionApi.updateSubmission(submissionId.value, {
          answers: formData.value,
          is_complete: false
        })
        
        console.log('✅ Form saved successfully')
        originalFormData.value = { ...formData.value }
      } catch (err) {
        console.error('❌ Error saving form:', err)
        error.value = 'Failed to save changes. Please try again.'
      } finally {
        saving.value = false
      }
    }

    const resetForm = () => {
      formData.value = { ...originalFormData.value }
      console.log('🔄 Form reset to original values')
    }

    const completeForm = async () => {
      if (!submissionId.value || isComplete.value) return
      
      // Check if all required fields are filled
      if (!allRequiredFieldsFilled.value) {
        error.value = 'Please fill in all required fields before completing the form.'
        setTimeout(() => {
          error.value = null
        }, 5000)
        return
      }
      
      saving.value = true
      try {
        console.log('🎯 Completing form submission:', submissionId.value)
        console.log('📝 Form data to submit:', formData.value)
        
        // Use the submitForm API which properly marks as complete
        const response = await submissionApi.submitForm(submissionId.value, formData.value)
        
        console.log('🎉 Form completion API response:', response.data)
        
        // Update local state from API response
        isComplete.value = response.data.is_complete || true
        completedDateTime.value = response.data.completed_datetime || new Date().toISOString()
        
        console.log('✅ Form submitted and marked as complete')
        console.log('📅 Completion time set to:', completedDateTime.value)
      } catch (err) {
        console.error('❌ Error completing form:', err)
        console.error('❌ Error response:', err.response?.data)
        error.value = 'Failed to complete form. Please try again.'
        setTimeout(() => {
          error.value = null
        }, 5000)
      } finally {
        saving.value = false
      }
    }

    const initializeFormData = async (formStructure, submissionIdParam) => {
      try {
        const existingAnswers = await loadSubmissionById(submissionIdParam)
        const initialData = {}
        
        console.log('📥 Loading existing answers:', existingAnswers)
        console.log('📥 Answer keys:', Object.keys(existingAnswers))
        
        const processQuestion = (question) => {
          console.log(`📝 Processing question: ${question.slug} (type: ${question.type})`)
          
          // Check if this is an address field using the proper function
          if (isAddressField(question)) {
            console.log(`🏠 Initializing address field: ${question.slug}`)
            const addressFields = ['street', 'city', 'state', 'postal_code', 'country']
            addressFields.forEach(field => {
              const flatKey = `${question.slug}__${field}`
              const value = existingAnswers[flatKey]
              initialData[flatKey] = value !== undefined ? value : ''
              console.log(`  ${flatKey}: "${initialData[flatKey]}" (found: ${value !== undefined})`)
            })
          } else {
            // Regular field initialization
            const value = existingAnswers[question.slug]
            initialData[question.slug] = value !== undefined ? value : (
              question.config?.multiple ? [] : ''
            )
            console.log(`  ${question.slug}: ${JSON.stringify(initialData[question.slug])} (found: ${value !== undefined})`)
          }
        }
        
        formStructure.pages.forEach(page => {
          // Process individual questions
          if (page.questions) {
            page.questions.forEach(processQuestion)
          }
          
          // Process questions from question groups
          if (page.question_groups) {
            page.question_groups.forEach(group => {
              if (group.questions) {
                group.questions.forEach(processQuestion)
              }
            })
          }
        })
        
        formData.value = initialData
        originalFormData.value = { ...initialData }
        
        console.log('🎯 Form data initialized for table editor:', initialData)
        console.log('🎯 Total fields:', Object.keys(initialData).length)
      } catch (err) {
        console.error('❌ Error initializing form data:', err)
        throw err
      }
    }

    // Auto-save functionality (using same pattern as DynamicForm.vue)
    const autoSaveFormData = async (data) => {
      if (!submissionId.value || !data) return
      
      try {
        await submissionApi.updateSubmission(submissionId.value, {
          answers: data,
          is_complete: false
        })
        console.log('📤 Form data auto-saved')
      } catch (err) {
        console.error('❌ Error auto-saving form data:', err)
      }
    }

    // Debounce utility function
    const debounce = (fn, delay) => {
      let timeoutId
      return (...args) => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(() => fn.apply(null, args), delay)
      }
    }

    const debouncedSave = debounce(autoSaveFormData, 2000)

    watch(
      () => formData.value,
      (newData) => {
        if (submissionId.value && newData && !isComplete.value) {
          debouncedSave(newData)
        }
      },
      { deep: true }
    )

    // Initialize on mount
    onMounted(async () => {
      try {
        const slug = route.params.slug
        const submissionIdParam = route.params.submissionId
        
        if (!slug) {
          error.value = 'Form slug is required'
          loading.value = false
          return
        }

        if (!submissionIdParam) {
          error.value = 'Submission ID is required for table editor'
          loading.value = false
          return
        }

        await loadQuestionTypes()
        const formStructure = await loadForm(slug)
        await initializeFormData(formStructure, submissionIdParam)
        
        loading.value = false
      } catch (err) {
        error.value = err.message || 'Failed to load form'
        loading.value = false
      }
    })

    // Tooltip methods
    const showTooltip = (tooltipId) => {
      activeTooltip.value = tooltipId
    }

    const hideTooltip = (tooltipId) => {
      if (activeTooltip.value === tooltipId) {
        activeTooltip.value = null
      }
    }

    const toggleTooltip = (tooltipId) => {
      if (activeTooltip.value === tooltipId) {
        activeTooltip.value = null
      } else {
        activeTooltip.value = tooltipId
      }
    }

    // Close tooltip when clicking outside
    const handleClickOutside = (event) => {
      if (activeTooltip.value && !event.target.closest('.relative')) {
        activeTooltip.value = null
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      // State
      form,
      formData,
      questionTypes,
      loading,
      error,
      saving,
      isComplete,
      completedDateTime,
      activeTooltip,
      
      // Computed
      isFormReady,
      allRequiredFieldsFilled,
      
      // Methods
      getFormKitType,
      getValidationRules,
      getQuestionPlaceholder,
      getQuestionOptions,
      getQuestionTypeConfig,
      getFormattedLabel,
      isAddressField,
      isRadioOrCheckbox,
      isSingleLineInput,
      getCountryOptions,
      updateField,
      isFieldDisabled,
      findPageForQuestion,
      getFormViewUrl,
      getAllQuestionsFromPage,
      getStateFieldVisibilityWrapper,
      getStateFieldRequiredWrapper,
      getStateFieldTypeWrapper,
      getStateFieldOptionsWrapper,
      getStateFieldPlaceholderWrapper,
      saveForm,
      resetForm,
      completeForm,
      showTooltip,
      hideTooltip,
      toggleTooltip
    }
  }
}
</script>

<style scoped>
/* Table-specific form styling */
:deep(.form-table-field) {
  margin-bottom: 0;
}

:deep(.form-table-wrapper) {
  margin-bottom: 0;
}

:deep(.form-table-input) {
  @apply text-sm;
}

/* Compact FormKit styling for table cells */
:deep(.formkit-outer) {
  margin-bottom: 0;
}

:deep(.formkit-wrapper) {
  margin-bottom: 0;
}

:deep(.formkit-help) {
  margin-top: 0.25rem;
  font-size: 0.75rem;
}

:deep(.formkit-messages) {
  margin-top: 0.25rem;
}

/* Radio and checkbox field alignment fix */
.radio-checkbox-field :deep(.formkit-outer) {
  margin-bottom: 0;
}

.radio-checkbox-field :deep(.formkit-fieldset) {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.radio-checkbox-field :deep(.formkit-wrapper) {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin: 0;
}

.radio-checkbox-field :deep(.formkit-options) {
  display: flex;
  gap: 2rem; /* More space between option groups */
  flex-direction: row;
  align-items: center;
}

.radio-checkbox-field :deep(.formkit-option) {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.25rem; /* Tight space between radio and its label */
}

.radio-checkbox-field :deep(.formkit-option-wrapper) {
  display: flex;
  align-items: center;
  gap: 0.25rem; /* Tight space between radio and its label */
}

.radio-checkbox-field :deep(.formkit-label) {
  margin-left: 0.25rem; /* Small gap between radio and label */
  margin-right: 0;
}

.radio-checkbox-field :deep(.formkit-legend) {
  display: none;
}

/* Address input styling for table */
:deep(.address-input) {
  @apply space-y-2;
}

:deep(.address-input .formkit-outer) {
  @apply mb-2;
}
</style>