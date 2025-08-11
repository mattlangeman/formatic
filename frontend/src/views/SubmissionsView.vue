<template>
  <div class="submissions-view">
    <div class="max-w-7xl mx-auto">
      <!-- Navigation breadcrumb -->
      <nav class="flex mb-6" aria-label="Breadcrumb">
        <ol class="inline-flex items-center space-x-1 md:space-x-3">
          <li class="inline-flex items-center">
            <router-link 
              to="/" 
              class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-primary-600"
            >
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              Forms
            </router-link>
          </li>
          
          <li>
            <div class="flex items-center">
              <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
              <router-link 
                :to="`/form/${formSlug}`" 
                class="ml-1 text-sm font-medium text-gray-700 hover:text-primary-600 md:ml-2"
              >
                {{ formName }}
              </router-link>
            </div>
          </li>
          
          <li aria-current="page">
            <div class="flex items-center">
              <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="ml-1 text-sm font-medium text-gray-500 md:ml-2">Submissions</span>
            </div>
          </li>
        </ol>
      </nav>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading submissions...</p>
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

      <!-- Submissions table -->
      <SubmissionsTable
        v-else
        :form-slug="formSlug"
        :form-name="formName"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { formApi } from '../services/api'
import SubmissionsTable from '../components/SubmissionsTable.vue'

export default {
  name: 'SubmissionsView',
  components: {
    SubmissionsTable
  },
  setup() {
    const route = useRoute()
    const formSlug = ref(route.params.slug)
    const formName = ref('')
    const loading = ref(true)
    const error = ref(null)

    const loadFormInfo = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Get form info to display name
        const response = await formApi.getForm(formSlug.value)
        formName.value = response.data.name
        
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to load form information'
        console.error('Error loading form:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadFormInfo()
    })

    return {
      formSlug,
      formName,
      loading,
      error
    }
  }
}
</script>

<style scoped>
.submissions-view {
  @apply p-6;
}
</style>