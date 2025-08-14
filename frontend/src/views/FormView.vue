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
        { label: 'All Forms', to: '/' }
      ]
      
      if (formName.value) {
        if (submissionId.value) {
          // Form submission path: All Forms > [Form Name] > Submissions > [Submission ID] > Form View
          items.push({ label: formName.value, to: `/form/${route.params.slug}` })
          items.push({ label: 'Submissions', to: `/form/${route.params.slug}/submissions` })
          items.push({ label: `Submission ${submissionId.value.substring(0, 8)}...`, to: `/form/${route.params.slug}/submission/${submissionId.value}/table` })
          items.push({ label: 'Form View', to: null })
        } else {
          // Regular form path: All Forms > [Form Name] > Fill Form
          items.push({ label: formName.value, to: `/form/${route.params.slug}` })
          items.push({ label: 'Fill Form', to: null })
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