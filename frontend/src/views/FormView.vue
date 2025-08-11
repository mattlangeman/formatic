<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb v-if="breadcrumbItems.length > 0" :items="breadcrumbItems" />

      <DynamicForm 
        :key="$route.params.slug" 
        :form-slug="$route.params.slug"
        @form-loaded="handleFormLoaded"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import DynamicForm from '../components/DynamicForm.vue'
import Breadcrumb from '../components/Breadcrumb.vue'

export default {
  name: 'FormView',
  components: {
    DynamicForm,
    Breadcrumb
  },
  setup() {
    const route = useRoute()
    const formName = ref('')
    const submissionId = ref(route.params.submissionId)
    
    const breadcrumbItems = computed(() => {
      const items = [
        { label: 'Forms', to: '/' }
      ]
      
      if (formName.value) {
        if (submissionId.value) {
          // Form submission path: Forms > [Form Name] > Submissions > [Submission ID]
          items.push({ label: formName.value, to: `/form/${route.params.slug}` })
          items.push({ label: 'Submissions', to: `/form/${route.params.slug}/submissions` })
          items.push({ label: `Submission ${submissionId.value.substring(0, 8)}...`, to: null })
        } else {
          // Regular form path: Forms > [Form Name]
          items.push({ label: formName.value, to: null })
        }
      }
      
      return items
    })
    
    const handleFormLoaded = (form) => {
      formName.value = form.name
    }
    
    return {
      breadcrumbItems,
      handleFormLoaded
    }
  }
}
</script>