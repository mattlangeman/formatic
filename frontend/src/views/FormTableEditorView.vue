<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb v-if="breadcrumbItems.length > 0" :items="breadcrumbItems" />
      
      <FormTableEditor @form-loaded="handleFormLoaded" />
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import FormTableEditor from '../components/FormTableEditor.vue'
import Breadcrumb from '../components/Breadcrumb.vue'

export default {
  name: 'FormTableEditorView',
  components: {
    FormTableEditor,
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
          // Table editor for submission: All Forms > [Form Name] > Submissions > [Submission ID] > Table View
          items.push({ label: formName.value, to: `/form/${route.params.slug}` })
          items.push({ label: 'Submissions', to: `/form/${route.params.slug}/submissions` })
          items.push({ label: `Submission ${submissionId.value.substring(0, 8)}...`, to: null })
          items.push({ label: 'Table View', to: null })
        } else {
          // Regular table editor: All Forms > [Form Name] > Table Editor
          items.push({ label: formName.value, to: `/form/${route.params.slug}` })
          items.push({ label: 'Table Editor', to: null })
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