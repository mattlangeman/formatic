<template>
  <div class="submissions-table">
    <!-- Header with title and actions -->
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900">
          {{ formName }} Submissions
        </h2>
        <p class="mt-1 text-sm text-gray-600">
          Total: {{ submissions.length }} submissions
          <span v-if="completedCount > 0" class="ml-3">
            ({{ completedCount }} completed, {{ inProgressCount }} in progress)
          </span>
        </p>
      </div>
      
      <div class="flex gap-3">
        <button
          @click="refreshSubmissions"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
        
        <button
          @click="exportToCSV"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export CSV
        </button>
      </div>
    </div>
    
    <!-- Filters -->
    <div class="mb-4 p-4 bg-gray-50 rounded-lg">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Search input -->
        <div>
          <label for="search" class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            id="search"
            placeholder="Search in submissions..."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        
        <!-- Status filter -->
        <div>
          <label for="status-filter" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="statusFilter"
            id="status-filter"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="all">All Submissions</option>
            <option value="completed">Completed Only</option>
            <option value="in_progress">In Progress Only</option>
          </select>
        </div>
        
        <!-- Clear filters button -->
        <div class="flex items-end">
          <button
            @click="resetFilters"
            v-if="searchQuery || statusFilter !== 'all'"
            class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-300">
          <thead class="bg-gray-50">
            <tr>
              <th 
                v-for="column in displayColumns" 
                :key="column.key"
                scope="col" 
                class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer hover:bg-gray-100"
                :class="column.class"
                @click="toggleSort(column.isAnswer ? 'answer_' + column.key : column.key)"
              >
                <div class="flex items-center justify-between">
                  <span>{{ column.label }}</span>
                  <span class="ml-2">
                    <svg
                      v-if="sortColumn === (column.isAnswer ? 'answer_' + column.key : column.key)"
                      class="w-4 h-4"
                      :class="sortDirection === 'asc' ? 'rotate-180' : ''"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    <svg
                      v-else
                      class="w-4 h-4 text-gray-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path fill-rule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-.707.293 1 1 0 01-.707-.293l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </span>
                </div>
              </th>
              <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="submission in paginatedSubmissions" :key="submission.id">
              <td 
                v-for="column in displayColumns" 
                :key="column.key"
                class="whitespace-nowrap px-3 py-4 text-sm"
                :class="column.class"
              >
                <div v-if="column.key === 'status'">
                  <span 
                    class="inline-flex rounded-full px-2 text-xs font-semibold leading-5"
                    :class="submission.is_complete ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                  >
                    {{ submission.is_complete ? 'Completed' : 'In Progress' }}
                  </span>
                </div>
                <div v-else-if="column.key === 'created_datetime'">
                  {{ formatDate(submission.created_datetime) }}
                </div>
                <div v-else-if="column.key === 'modified_datetime'">
                  {{ formatDate(submission.modified_datetime) }}
                </div>
                <div v-else-if="column.key === 'completed_datetime'">
                  {{ submission.completed_datetime ? formatDate(submission.completed_datetime) : '-' }}
                </div>
                <div v-else-if="column.key === 'form_version_number'">
                  <span class="inline-flex rounded-full px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800">
                    v{{ submission.form_version_number || '1' }}
                  </span>
                </div>
                <div v-else-if="column.isAnswer">
                  {{ getAnswerValue(submission, column.key) }}
                </div>
                <div v-else>
                  {{ submission[column.key] || '-' }}
                </div>
              </td>
              <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                <div class="flex justify-end gap-2">
                  <button
                    @click="viewSubmission(submission)"
                    class="inline-flex items-center px-2.5 py-1.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 hover:bg-primary-200 transition-colors duration-200"
                  >
                    View
                  </button>
                  <button
                    @click="tableViewSubmission(submission)"
                    class="inline-flex items-center px-2.5 py-1.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors duration-200"
                    title="Edit in Table View"
                  >
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0V4a2 2 0 012-2h14a2 2 0 012 2v16a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                    </svg>
                    Table
                  </button>
                  <button
                    @click="continueSubmission(submission)"
                    class="inline-flex items-center px-2.5 py-1.5 rounded-full text-xs font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors duration-200"
                  >
                    {{ submission.is_complete ? 'View' : 'Continue' }}
                  </button>
                </div>
              </td>
            </tr>
            
            <tr v-if="filteredSubmissions.length === 0">
              <td :colspan="displayColumns.length + 1" class="px-3 py-8 text-center text-sm text-gray-500">
                {{ submissions.length === 0 ? 'No submissions found' : 'No submissions match your filters' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-4">
      <div class="flex flex-1 justify-between sm:hidden">
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
          class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
      
      <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-gray-700">
            Showing
            <span class="font-medium">{{ startIndex + 1 }}</span>
            to
            <span class="font-medium">{{ Math.min(endIndex, filteredSubmissions.length) }}</span>
            of
            <span class="font-medium">{{ filteredSubmissions.length }}</span>
            results{{ searchQuery || statusFilter !== 'all' ? ' (filtered)' : '' }}
          </p>
        </div>
        
        <div>
          <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">Previous</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" />
              </svg>
            </button>
            
            <button
              v-for="page in displayPages"
              :key="page"
              @click="goToPage(page)"
              :class="[
                page === currentPage 
                  ? 'z-10 bg-primary-600 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600'
                  : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:outline-offset-0',
                'relative inline-flex items-center px-4 py-2 text-sm font-semibold focus:z-20'
              ]"
            >
              {{ page }}
            </button>
            
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">Next</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
              </svg>
            </button>
          </nav>
        </div>
      </div>
    </div>

    <!-- View Submission Modal -->
    <div v-if="selectedSubmission" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="selectedSubmission = null"></div>
        
        <div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl">
          <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg font-semibold leading-6 text-gray-900 mb-4">
                  Submission Details
                </h3>
                
                <div class="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p class="text-sm font-medium text-gray-500">Status</p>
                    <p class="mt-1">
                      <span 
                        class="inline-flex rounded-full px-2 text-xs font-semibold leading-5"
                        :class="selectedSubmission.is_complete ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                      >
                        {{ selectedSubmission.is_complete ? 'Completed' : 'In Progress' }}
                      </span>
                    </p>
                  </div>
                  
                  <div>
                    <p class="text-sm font-medium text-gray-500">Started</p>
                    <p class="mt-1 text-sm">{{ formatDate(selectedSubmission.created_datetime) }}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm font-medium text-gray-500">Last Updated</p>
                    <p class="mt-1 text-sm">{{ formatDate(selectedSubmission.modified_datetime) }}</p>
                  </div>
                  
                  <div v-if="selectedSubmission.user_email">
                    <p class="text-sm font-medium text-gray-500">Email</p>
                    <p class="mt-1 text-sm">{{ selectedSubmission.user_email }}</p>
                  </div>
                  
                  <!-- Completed datetime removed as it's redundant with Last Updated for completed forms -->
                </div>
                
                <div class="border-t border-gray-200 pt-4">
                  <h4 class="text-sm font-medium text-gray-900 mb-3">Answers</h4>
                  <div class="space-y-3 max-h-96 overflow-y-auto">
                    <div v-for="[key, value, question] in sortedAnswers" :key="key" class="flex justify-between py-2 border-b border-gray-100">
                      <span class="text-sm font-medium text-gray-500">
                        {{ question?.text || formatFieldName(key) }}
                      </span>
                      <span class="text-sm text-gray-900">{{ formatAnswerValue(value) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
            <button
              type="button"
              @click="selectedSubmission = null"
              class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 sm:ml-3 sm:w-auto"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { submissionApi, formApi } from '../services/api'

export default {
  name: 'SubmissionsTable',
  props: {
    formSlug: {
      type: String,
      required: true
    },
    formName: {
      type: String,
      default: 'Form'
    }
  },
  setup(props) {
    const router = useRouter()
    const route = useRoute()
    const submissions = ref([])
    const formStructure = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const selectedSubmission = ref(null)
    
    // Initialize sorting and filtering state from URL query parameters
    const sortColumn = ref(route.query.sort || 'modified_datetime')
    const sortDirection = ref(route.query.dir || 'desc') // 'asc' or 'desc'
    const searchQuery = ref(route.query.search || '')
    const statusFilter = ref(route.query.status || 'all') // 'all', 'completed', 'in_progress'

    // Get key fields to display in the table
    const displayColumns = computed(() => {
      const columns = [
        { key: 'status', label: 'Status' },
        { key: 'created_datetime', label: 'Started' },
        { key: 'modified_datetime', label: 'Last Updated' },
        { key: 'form_version_number', label: 'Version' },
      ]

      // Add only the first question as a column
      if (formStructure.value?.pages?.length > 0) {
        const firstPage = formStructure.value.pages[0]
        if (firstPage.questions?.length > 0) {
          const firstQuestion = firstPage.questions[0]
          columns.push({
            key: firstQuestion.slug,
            label: firstQuestion.text || formatFieldName(firstQuestion.slug),
            isAnswer: true
          })
        }
      }

      // Don't show completed_datetime as it's redundant with modified_datetime
      // columns.push({ key: 'completed_datetime', label: 'Completed' })
      
      return columns
    })

    const completedCount = computed(() => {
      return submissions.value.filter(s => s.is_complete).length
    })

    const inProgressCount = computed(() => {
      return submissions.value.filter(s => !s.is_complete).length
    })
    
    // Sorting function
    const toggleSort = (column) => {
      if (sortColumn.value === column) {
        // Toggle direction if same column
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      } else {
        // New column, default to ascending
        sortColumn.value = column
        sortDirection.value = 'asc'
      }
    }
    
    // Update URL when filters or sorting change
    const updateURL = () => {
      const query = {}
      
      // Add sorting params (only if not default)
      if (sortColumn.value !== 'modified_datetime') {
        query.sort = sortColumn.value
      }
      if (sortDirection.value !== 'desc') {
        query.dir = sortDirection.value
      }
      
      // Add filter params (only if they have values)
      if (searchQuery.value) {
        query.search = searchQuery.value
      }
      
      if (statusFilter.value !== 'all') {
        query.status = statusFilter.value
      }
      
      // Update URL without navigation (replace current history entry)
      router.replace({ 
        name: route.name,
        params: route.params,
        query: query
      })
    }
    
    // Watch for changes in filters/sorting and update URL
    watch([searchQuery, statusFilter, sortColumn, sortDirection], () => {
      updateURL()
      // Reset to first page when filters change (but not when just sorting)
      if (searchQuery.value || statusFilter.value !== 'all') {
        currentPage.value = 1
      }
    })
    
    // Watch for URL changes and update filters/sorting accordingly
    watch(
      () => route.query,
      (newQuery) => {
        sortColumn.value = newQuery.sort || 'modified_datetime'
        sortDirection.value = newQuery.dir || 'desc'
        searchQuery.value = newQuery.search || ''
        statusFilter.value = newQuery.status || 'all'
      }
    )
    
    // Reset filters
    const resetFilters = () => {
      searchQuery.value = ''
      statusFilter.value = 'all'
      currentPage.value = 1
      // updateURL will be called automatically via the watcher
    }

    const totalPages = computed(() => {
      return Math.ceil(filteredSubmissions.value.length / itemsPerPage.value)
    })

    const startIndex = computed(() => {
      return (currentPage.value - 1) * itemsPerPage.value
    })

    const endIndex = computed(() => {
      return startIndex.value + itemsPerPage.value
    })

    // Filtered submissions based on search and status
    const filteredSubmissions = computed(() => {
      let filtered = [...submissions.value]
      
      // Apply status filter
      if (statusFilter.value === 'completed') {
        filtered = filtered.filter(s => s.is_complete)
      } else if (statusFilter.value === 'in_progress') {
        filtered = filtered.filter(s => !s.is_complete)
      }
      
      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(submission => {
          // Search in email
          if (submission.user_email?.toLowerCase().includes(query)) return true
          
          // Search in answers
          if (submission.answers) {
            const answersStr = JSON.stringify(submission.answers).toLowerCase()
            if (answersStr.includes(query)) return true
          }
          
          // Search in ID
          if (submission.id.toLowerCase().includes(query)) return true
          
          return false
        })
      }
      
      return filtered
    })
    
    // Sorted submissions
    const sortedSubmissions = computed(() => {
      const sorted = [...filteredSubmissions.value]
      
      sorted.sort((a, b) => {
        let aVal = a[sortColumn.value]
        let bVal = b[sortColumn.value]
        
        // Handle nested answer values
        if (sortColumn.value.includes('answer_')) {
          const key = sortColumn.value.replace('answer_', '')
          aVal = a.answers?.[key]
          bVal = b.answers?.[key]
        }
        
        // Handle status column
        if (sortColumn.value === 'status') {
          aVal = a.is_complete ? 'Completed' : 'In Progress'
          bVal = b.is_complete ? 'Completed' : 'In Progress'
        }
        
        // Handle null/undefined values
        if (aVal == null) aVal = ''
        if (bVal == null) bVal = ''
        
        // Sort based on data type
        if (sortColumn.value.includes('datetime')) {
          // Date sorting
          aVal = new Date(aVal)
          bVal = new Date(bVal)
        } else if (typeof aVal === 'string') {
          // String sorting (case-insensitive)
          aVal = aVal.toString().toLowerCase()
          bVal = bVal.toString().toLowerCase()
        }
        
        // Perform comparison
        if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
        if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1
        return 0
      })
      
      return sorted
    })
    
    const paginatedSubmissions = computed(() => {
      return sortedSubmissions.value.slice(startIndex.value, endIndex.value)
    })

    const displayPages = computed(() => {
      const pages = []
      const maxDisplay = 5
      let start = Math.max(1, currentPage.value - Math.floor(maxDisplay / 2))
      let end = Math.min(totalPages.value, start + maxDisplay - 1)
      
      if (end - start < maxDisplay - 1) {
        start = Math.max(1, end - maxDisplay + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    // Get sorted answers based on form structure (page and question order)
    const sortedAnswers = computed(() => {
      if (!selectedSubmission.value?.answers || !formStructure.value) {
        return Object.entries(selectedSubmission.value?.answers || {})
      }

      const answers = selectedSubmission.value.answers

      // Create a map of question slugs to their order
      const questionOrder = new Map()
      let orderIndex = 0

      formStructure.value.pages.forEach((page, pageIndex) => {
        page.questions.forEach((question, questionIndex) => {
          questionOrder.set(question.slug, {
            pageIndex,
            questionIndex,
            orderIndex: orderIndex++,
            question
          })
        })
      })

      // Sort answers by form structure order
      const answersWithOrder = Object.entries(answers).map(([key, value]) => {
        const orderInfo = questionOrder.get(key)
        return {
          key,
          value,
          order: orderInfo ? orderInfo.orderIndex : 999999, // Put unknown fields at end
          question: orderInfo?.question
        }
      })

      // Sort by order and return as [key, value] entries
      return answersWithOrder
        .sort((a, b) => a.order - b.order)
        .map(item => [item.key, item.value, item.question])
    })

    const loadSubmissions = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Load both submissions and form structure
        const [submissionsResponse, formResponse] = await Promise.all([
          submissionApi.getSubmissionsByForm(props.formSlug),
          formApi.getForm(props.formSlug)
        ])
        
        // Sort submissions by modified_datetime (most recent first)
        submissions.value = submissionsResponse.data.sort((a, b) => {
          return new Date(b.modified_datetime) - new Date(a.modified_datetime)
        })
        formStructure.value = formResponse.data
        
        console.log(`📊 Loaded ${submissions.value.length} submissions for ${props.formSlug}`)
        console.log(`📋 Loaded form structure with ${formStructure.value.pages.length} pages`)
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to load submissions'
        console.error('Error loading submissions:', err)
      } finally {
        loading.value = false
      }
    }

    const refreshSubmissions = () => {
      loadSubmissions()
    }

    const viewSubmission = (submission) => {
      selectedSubmission.value = submission
    }

    const continueSubmission = (submission) => {
      // Navigate directly to the submission URL
      if (submission.is_complete) {
        // View completed submission
        router.push({ 
          name: 'form-submission',
          params: { 
            slug: props.formSlug,
            submissionId: submission.id
          }
        })
      } else {
        // Continue incomplete submission
        router.push({ 
          name: 'form-submission',
          params: { 
            slug: props.formSlug,
            submissionId: submission.id
          }
        })
      }
    }

    const tableViewSubmission = (submission) => {
      // Navigate directly to the table view of the submission
      router.push({ 
        name: 'form-submission-table',
        params: { 
          slug: props.formSlug,
          submissionId: submission.id
        }
      })
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      // Format without seconds: MM/DD/YYYY HH:MM AM/PM
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    const formatFieldName = (fieldName) => {
      // Convert snake_case or kebab-case to Title Case
      return fieldName
        .replace(/[-_]/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatAnswerValue = (value) => {
      if (value === null || value === undefined || value === '') {
        return '-'
      }
      if (typeof value === 'object') {
        return JSON.stringify(value)
      }
      return value
    }

    const getAnswerValue = (submission, key) => {
      return formatAnswerValue(submission.answers?.[key])
    }

    const exportToCSV = () => {
      const dataToExport = filteredSubmissions.value
      if (dataToExport.length === 0) {
        alert('No data to export')
        return
      }

      // Collect all unique field names
      const allFields = new Set()
      dataToExport.forEach(submission => {
        Object.keys(submission.answers || {}).forEach(key => {
          allFields.add(key)
        })
      })

      // Build CSV header
      const headers = ['ID', 'Status', 'Started', 'Last Updated', 'Version', 'Email', ...Array.from(allFields)]
      const csvRows = [headers.join(',')]

      // Build CSV rows
      dataToExport.forEach(submission => {
        const row = [
          submission.id,
          submission.is_complete ? 'Completed' : 'In Progress',
          submission.created_datetime,
          submission.modified_datetime || '',
          `v${submission.form_version_number || '1'}`,
          submission.user_email || '',
          ...Array.from(allFields).map(field => {
            const value = submission.answers?.[field] || ''
            // Escape values containing commas
            return typeof value === 'string' && value.includes(',') 
              ? `"${value.replace(/"/g, '""')}"` 
              : value
          })
        ]
        csvRows.push(row.join(','))
      })

      // Download CSV
      const csvContent = csvRows.join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      
      link.setAttribute('href', url)
      const isFiltered = searchQuery.value || statusFilter.value !== 'all'
      const filename = `${props.formSlug}_submissions${isFiltered ? '_filtered' : ''}_${new Date().toISOString().split('T')[0]}.csv`
      link.setAttribute('download', filename)
      link.style.visibility = 'hidden'
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    const goToPage = (page) => {
      currentPage.value = page
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }

    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    onMounted(() => {
      loadSubmissions()
    })

    return {
      submissions,
      loading,
      error,
      currentPage,
      itemsPerPage,
      selectedSubmission,
      displayColumns,
      completedCount,
      inProgressCount,
      totalPages,
      startIndex,
      endIndex,
      paginatedSubmissions,
      filteredSubmissions,
      displayPages,
      sortedAnswers,
      refreshSubmissions,
      viewSubmission,
      continueSubmission,
      tableViewSubmission,
      formatDate,
      formatFieldName,
      formatAnswerValue,
      getAnswerValue,
      exportToCSV,
      goToPage,
      nextPage,
      previousPage,
      // Sorting and filtering
      sortColumn,
      sortDirection,
      searchQuery,
      statusFilter,
      toggleSort,
      resetFilters
    }
  }
}
</script>

<style scoped>
.submissions-table {
  @apply p-6;
}
</style>