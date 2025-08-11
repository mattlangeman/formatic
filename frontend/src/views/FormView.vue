<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <div class="mb-6">
        <router-link 
          to="/"
          class="inline-flex items-center text-primary-600 hover:text-primary-700 transition-colors"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Forms
        </router-link>
      </div>

      <DynamicForm :key="$route.params.slug" :form-slug="$route.params.slug" />
    </div>
  </div>
</template>

<script>
import DynamicForm from '../components/DynamicForm.vue'

export default {
  name: 'FormView',
  components: {
    DynamicForm
  }
}
</script>