<template>
  <div class="submissions-view">
    <div class="max-w-7xl mx-auto">
      <!-- Navigation breadcrumb -->
      <Breadcrumb :items="breadcrumbItems" />

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
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { formApi } from '../services/api'
import SubmissionsTable from '../components/SubmissionsTable.vue'
import Breadcrumb from '../components/Breadcrumb.vue'

export default {
  name: 'SubmissionsView',
  components: {
    SubmissionsTable,
    Breadcrumb
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

    const breadcrumbItems = computed(() => [
      { label: 'Forms', to: '/' },
      { label: formName.value || 'Form', to: `/form/${formSlug.value}` },
      { label: 'Submissions', to: null } // Current page, no link
    ])

    onMounted(() => {
      loadFormInfo()
    })

    return {
      formSlug,
      formName,
      loading,
      error,
      breadcrumbItems
    }
  }
}
</script>

<style scoped>
.submissions-view {
  @apply p-6;
}
</style>