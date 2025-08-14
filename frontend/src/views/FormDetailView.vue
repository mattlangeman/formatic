<template>
  <div class="form-detail-view">
    <div class="max-w-7xl mx-auto">
      <!-- Navigation breadcrumb -->
      <Breadcrumb :items="breadcrumbItems" />

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading form details...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="text-center py-12">
        <div class="text-red-600 mb-4">
          <svg class="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.96-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <p class="text-red-600 font-medium">{{ error }}</p>
      </div>

      <!-- Form Details Content -->
      <div v-else class="space-y-6">
        <!-- Header Section -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">{{ form.name }}</h1>
              <p v-if="form.description" class="mt-2 text-gray-600">{{ form.description }}</p>
            </div>
            <span
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
              :class="form.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
            >
              {{ form.is_active ? 'Published' : 'Draft' }}
            </span>
          </div>

          <!-- Form Metadata -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div>
              <p class="text-sm font-medium text-gray-500">Form Slug</p>
              <p class="mt-1 text-sm text-gray-900 font-mono">{{ form.slug }}</p>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-500">Form ID</p>
              <p class="mt-1 text-sm text-gray-900 font-mono text-xs">{{ form.id }}</p>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-500">Current Version</p>
              <p class="mt-1 text-sm text-gray-900 font-semibold">
                {{ currentVersion ? `v${currentVersion.version_number}` : 'No versions' }}
              </p>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-500">Total Versions</p>
              <p class="mt-1 text-sm text-gray-900 font-semibold">{{ totalVersions }}</p>
            </div>
          </div>
        </div>

        <!-- Metrics Section -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">📊 Metrics</h2>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="text-center">
              <p class="text-3xl font-bold text-primary-600">{{ submissionStats.total || 0 }}</p>
              <p class="text-sm text-gray-600 mt-1">Total Submissions</p>
            </div>
            <div class="text-center">
              <p class="text-3xl font-bold text-green-600">{{ submissionStats.completed || 0 }}</p>
              <p class="text-sm text-gray-600 mt-1">Completed</p>
            </div>
            <div class="text-center">
              <p class="text-3xl font-bold text-yellow-600">{{ submissionStats.in_progress || 0 }}</p>
              <p class="text-sm text-gray-600 mt-1">In Progress</p>
            </div>
            <div class="text-center">
              <p class="text-3xl font-bold text-blue-600">{{ completionRate }}%</p>
              <p class="text-sm text-gray-600 mt-1">Completion Rate</p>
            </div>
          </div>

          <!-- Average completion time if available -->
          <div v-if="submissionStats.avg_completion_time" class="mt-6 pt-6 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Average Completion Time</span>
              <span class="text-sm font-medium text-gray-900">{{ formatTime(submissionStats.avg_completion_time) }}</span>
            </div>
          </div>
        </div>

        <!-- Form Structure Section -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">📝 Form Structure</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span class="text-sm text-gray-600">Pages</span>
              <span class="text-sm font-medium text-gray-900">{{ form.pages?.length || 0 }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span class="text-sm text-gray-600">Total Questions</span>
              <span class="text-sm font-medium text-gray-900">{{ totalQuestions }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span class="text-sm text-gray-600">Required Fields</span>
              <span class="text-sm font-medium text-gray-900">{{ requiredFields }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span class="text-sm text-gray-600">Conditional Logic</span>
              <span class="text-sm font-medium text-gray-900">{{ conditionalFields }} branches</span>
            </div>
          </div>

          <!-- Page breakdown -->
          <div v-if="form.pages && form.pages.length > 0" class="mt-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Page Breakdown</h3>
            <div class="space-y-2">
              <div v-for="(page, index) in form.pages" :key="page.id" class="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                <span class="text-sm text-gray-600">{{ index + 1 }}. {{ page.name || `Page ${index + 1}` }}</span>
                <span class="text-xs text-gray-500">{{ page.questions?.length || 0 }} questions</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Version History Section -->
        <div v-if="versions.length > 0" class="bg-white shadow rounded-lg p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">📋 Version History</h2>
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created By</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="version in versions" :key="version.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <span class="text-sm font-medium text-gray-900">v{{ version.version_number }}</span>
                      <span v-if="currentVersion && version.id === currentVersion.id" class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Current
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="version.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                      {{ version.is_published ? 'Published' : 'Draft' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm text-gray-900 max-w-xs truncate" :title="version.notes">
                      {{ version.notes || 'No notes' }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(version.created_datetime) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ version.created_by || 'Unknown' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Actions Section -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">🔗 Actions</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <router-link
              :to="{ name: 'submissions', params: { slug: form.slug } }"
              class="flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v7m3-2h6" />
              </svg>
              View Submissions
            </router-link>

            <router-link
              :to="{ name: 'form-builder', params: { slug: form.slug } }"
              class="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              Edit Form
            </router-link>

            <a
              :href="`/form/${form.slug}/fill`"
              target="_blank"
              class="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Preview Form
            </a>

            <button
              @click="copyShareLink"
              class="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m9.032 4.026a9.001 9.001 0 01-7.432 0m9.032-4.026A9.001 9.001 0 0112 3c-4.474 0-8.268 2.943-9.543 7a9.97 9.97 0 011.827 3.342M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ copiedLink ? 'Copied!' : 'Share Link' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { formBuilderApi, submissionApi, formApi } from '../services/api'
import Breadcrumb from '../components/Breadcrumb.vue'

export default {
  name: 'FormDetailView',
  components: {
    Breadcrumb
  },
  setup() {
    const route = useRoute()
    const formSlug = ref(route.params.slug)
    const form = ref({})
    const submissionStats = ref({})
    const versions = ref([])
    const loading = ref(true)
    const error = ref(null)
    const copiedLink = ref(false)

    const breadcrumbItems = computed(() => [
      { label: 'All Forms', to: '/' },
      { label: form.value.name || 'Form Details', to: null }
    ])

    const totalQuestions = computed(() => {
      if (!form.value.pages) return 0
      return form.value.pages.reduce((total, page) => {
        return total + (page.questions?.length || 0)
      }, 0)
    })

    const requiredFields = computed(() => {
      if (!form.value.pages) return 0
      return form.value.pages.reduce((total, page) => {
        return total + (page.questions?.filter(q => q.is_required)?.length || 0)
      }, 0)
    })

    const conditionalFields = computed(() => {
      if (!form.value.pages) return 0
      let count = 0
      form.value.pages.forEach(page => {
        if (page.conditional_logic) count++
        page.questions?.forEach(q => {
          if (q.conditional_logic) count++
        })
      })
      return count
    })

    const completionRate = computed(() => {
      if (!submissionStats.value.total) return 0
      return Math.round((submissionStats.value.completed / submissionStats.value.total) * 100)
    })

    const currentVersion = computed(() => {
      // Find the latest published version (highest version number among published versions)
      const publishedVersions = versions.value.filter(v => v.is_published)
      if (publishedVersions.length > 0) {
        return publishedVersions.reduce((latest, current) => 
          current.version_number > latest.version_number ? current : latest
        )
      }
      return versions.value[0] // Return latest version if no published versions
    })

    const totalVersions = computed(() => {
      return versions.value.length
    })

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatTime = (seconds) => {
      if (!seconds) return 'N/A'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }

    const copyShareLink = async () => {
      const link = `${window.location.origin}/form/${formSlug.value}/fill`
      try {
        await navigator.clipboard.writeText(link)
        copiedLink.value = true
        setTimeout(() => {
          copiedLink.value = false
        }, 2000)
      } catch (err) {
        console.error('Failed to copy link:', err)
      }
    }

    const loadFormDetails = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Load form details using the builder API
        const formResponse = await formBuilderApi.getBuilderForm(formSlug.value)
        form.value = formResponse.data
        
        // Load form versions
        try {
          const versionsResponse = await formApi.getFormVersions(formSlug.value)
          versions.value = versionsResponse.data.sort((a, b) => b.version_number - a.version_number)
        } catch (err) {
          console.warn('Could not load version data:', err)
          versions.value = []
        }
        
        // Load submission statistics
        try {
          // Try to get stats endpoint first
          const statsResponse = await submissionApi.getSubmissionStats(formSlug.value)
          submissionStats.value = statsResponse.data
        } catch (err) {
          // If stats endpoint doesn't exist, calculate from submissions list
          try {
            const submissionsResponse = await submissionApi.getSubmissionsByForm(formSlug.value)
            const submissions = submissionsResponse.data
            
            submissionStats.value = {
              total: submissions.length,
              completed: submissions.filter(s => s.is_complete).length,
              in_progress: submissions.filter(s => !s.is_complete).length
            }
          } catch (submissionErr) {
            // If both fail, just show zeros
            console.warn('Could not load submission data:', submissionErr)
            submissionStats.value = { total: 0, completed: 0, in_progress: 0 }
          }
        }
        
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to load form details'
        console.error('Error loading form details:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadFormDetails()
    })

    return {
      formSlug,
      form,
      submissionStats,
      versions,
      loading,
      error,
      breadcrumbItems,
      totalQuestions,
      requiredFields,
      conditionalFields,
      completionRate,
      currentVersion,
      totalVersions,
      copiedLink,
      formatDate,
      formatTime,
      copyShareLink
    }
  }
}
</script>

<style scoped>
.form-detail-view {
  @apply p-6;
}
</style>