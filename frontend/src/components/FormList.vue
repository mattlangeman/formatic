<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Available Forms</h1>
      <p class="text-lg text-gray-600">Select a form to get started</p>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading forms...</p>
    </div>

    <div v-else-if="error" class="text-center py-12">
      <div class="text-red-600 mb-4">
        <svg class="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.96-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <p class="text-red-600 font-medium">{{ error }}</p>
      <button
        @click="loadForms"
        class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Try Again
      </button>
    </div>

    <div v-else-if="forms.length === 0" class="text-center py-12">
      <svg class="h-12 w-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-500 text-lg">No forms available at the moment</p>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="form in forms"
        :key="form.id"
        class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-200"
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-gray-900">{{ form.name }}</h3>
            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="form.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
            >
              {{ form.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>

          <div class="mb-4">
            <p v-if="form.description" class="text-gray-600 text-sm mb-3">
              {{ form.description }}
            </p>

            <div class="flex items-center text-sm text-gray-500 space-x-4">
              <span class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {{ form.pages?.length || 0 }} {{ form.pages?.length === 1 ? 'page' : 'pages' }}
              </span>

              <span class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ getTotalQuestions(form) }} {{ getTotalQuestions(form) === 1 ? 'question' : 'questions' }}
              </span>
            </div>

            <div v-if="submissionStats[form.slug]" class="mt-3 pt-3 border-t border-gray-200">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">
                  <span class="font-medium">{{ submissionStats[form.slug].total }}</span> submissions
                </span>
                <span class="text-green-600">
                  <span class="font-medium">{{ submissionStats[form.slug].completed }}</span> completed
                </span>
              </div>
            </div>
          </div>

          <div class="flex gap-2">
            <router-link
              :to="{ name: 'form', params: { slug: form.slug } }"
              class="flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
            >
              Start New Form
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </router-link>

            <router-link
              :to="{ name: 'submissions', params: { slug: form.slug } }"
              class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
              title="View Submissions"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v7m3-2h6" />
              </svg>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { formApi, submissionApi } from '../services/api'

export default {
  name: 'FormList',
  setup() {
    const forms = ref([])
    const loading = ref(true)
    const error = ref(null)
    const submissionStats = ref({})

    const loadForms = async () => {
      try {
        loading.value = true
        error.value = null

        const response = await formApi.getForms()
        forms.value = response.data

        // Load submission statistics for each form
        await loadSubmissionStats()

      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to load forms'
        console.error('Error loading forms:', err)
      } finally {
        loading.value = false
      }
    }

    const getTotalQuestions = (form) => {
      if (!form.pages) return 0
      return form.pages.reduce((total, page) => total + (page.questions?.length || 0), 0)
    }

    const loadSubmissionStats = async () => {
      const stats = {}

      // Load submissions for each form in parallel
      const promises = forms.value.map(async (form) => {
        try {
          const response = await submissionApi.getSubmissionsByForm(form.slug)
          const submissions = response.data

          stats[form.slug] = {
            total: submissions.length,
            completed: submissions.filter(s => s.is_complete).length
          }
        } catch (err) {
          console.error(`Error loading submissions for ${form.slug}:`, err)
          stats[form.slug] = { total: 0, completed: 0 }
        }
      })

      await Promise.all(promises)
      submissionStats.value = stats
    }

    onMounted(() => {
      loadForms()
    })

    return {
      forms,
      loading,
      error,
      submissionStats,
      loadForms,
      getTotalQuestions
    }
  }
}
</script>