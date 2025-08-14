<template>
  <div class="new-form-view min-h-screen bg-gray-50">
    <div class="max-w-2xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Create New Form</h1>
        <p class="mt-2 text-lg text-gray-600">
          Start building your dynamic form with our drag-and-drop builder
        </p>
      </div>

      <!-- Form Creation Card -->
      <div class="bg-white shadow-lg rounded-lg overflow-hidden">
        <div class="px-6 py-8">
          <form @submit.prevent="createForm">
            <div class="space-y-6">
              <!-- Form Name -->
              <div>
                <label for="form-name" class="block text-sm font-medium text-gray-700 mb-2">
                  Form Name
                  <span class="text-red-500">*</span>
                </label>
                <input
                  id="form-name"
                  v-model="formData.name"
                  type="text"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
                  placeholder="My Awesome Form"
                  @input="generateSlug"
                />
              </div>

              <!-- Form Slug -->
              <div>
                <label for="form-slug" class="block text-sm font-medium text-gray-700 mb-2">
                  Form Slug
                  <span class="text-gray-500 text-xs">(URL identifier)</span>
                </label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 text-lg">
                    /form/
                  </span>
                  <input
                    id="form-slug"
                    v-model="formData.slug"
                    type="text"
                    required
                    pattern="[a-z0-9-]+"
                    class="w-full pl-20 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
                    placeholder="my-awesome-form"
                  />
                </div>
                <p class="mt-1 text-xs text-gray-500">
                  Only lowercase letters, numbers, and hyphens allowed
                </p>
              </div>

              <!-- Options -->
              <div class="space-y-4">
                <h3 class="text-lg font-medium text-gray-900">Options</h3>
                
                <div class="space-y-3">
                  <label class="flex items-center">
                    <input
                      v-model="formData.skipDefaultPage"
                      type="checkbox"
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    />
                    <span class="ml-3 text-sm text-gray-700">
                      Start with empty form (don't create default page)
                    </span>
                  </label>
                </div>
              </div>

              <!-- Template Selection (Future Enhancement) -->
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-blue-800">Coming Soon: Form Templates</h3>
                    <p class="mt-1 text-sm text-blue-700">
                      Soon you'll be able to start from pre-built templates for common form types like surveys, contact forms, and registrations.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="mt-8 flex justify-end space-x-4">
              <button
                type="button"
                @click="$router.go(-1)"
                class="px-6 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isCreating || !formData.name.trim() || !formData.slug.trim()"
                class="px-6 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed"
              >
                <span v-if="isCreating" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </span>
                <span v-else>Create Form & Start Building</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Benefits Section -->
      <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="text-center">
          <div class="mx-auto h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"/>
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-medium text-gray-900">Drag & Drop Builder</h3>
          <p class="mt-2 text-sm text-gray-600">
            Easily add questions by dragging them from the question palette onto your form pages.
          </p>
        </div>

        <div class="text-center">
          <div class="mx-auto h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-medium text-gray-900">Multiple Question Types</h3>
          <p class="mt-2 text-sm text-gray-600">
            Text inputs, dropdowns, yes/no questions, address fields, and more.
          </p>
        </div>

        <div class="text-center">
          <div class="mx-auto h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-medium text-gray-900">Version Control</h3>
          <p class="mt-2 text-sm text-gray-600">
            Publish versions of your form and track changes over time.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { formBuilderApi } from '../services/api.js'

const router = useRouter()

// Reactive data
const formData = ref({
  name: '',
  slug: '',
  skipDefaultPage: false
})
const isCreating = ref(false)

// Generate slug from name
const generateSlug = () => {
  if (formData.value.name && !formData.value.slug) {
    formData.value.slug = formData.value.name
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single
      .trim()
  }
}

// Create form
const createForm = async () => {
  if (isCreating.value) return
  
  isCreating.value = true
  
  try {
    const response = await formBuilderApi.createForm({
      name: formData.value.name.trim(),
      slug: formData.value.slug.trim(),
      skip_default_page: formData.value.skipDefaultPage
    })
    
    // Redirect to form builder
    router.push(`/builder/${response.data.slug}`)
  } catch (error) {
    console.error('Failed to create form:', error)
    
    // Handle specific error cases
    if (error.response?.status === 400) {
      const errorData = error.response.data
      if (errorData.slug && errorData.slug.includes('already exists')) {
        alert('A form with this slug already exists. Please choose a different slug.')
      } else {
        alert('Please check your form data and try again.')
      }
    } else {
      alert('Failed to create form. Please try again.')
    }
  } finally {
    isCreating.value = false
  }
}
</script>

<style scoped>
.new-form-view {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

input:focus {
  outline: none;
}

/* Custom focus styles for better accessibility */
input:focus,
button:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
</style>