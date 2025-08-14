<template>
  <div class="publish-modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="publish-modal bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <!-- Header -->
      <div class="modal-header p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">Publish Form</h2>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <p class="mt-2 text-sm text-gray-500">
          Create a new published version of "{{ form.name }}"
        </p>
      </div>

      <!-- Content -->
      <div class="modal-content p-6">
        <form @submit.prevent="handlePublish">
          <div class="space-y-4">
            <!-- Version Notes -->
            <div>
              <label for="notes" class="block text-sm font-medium text-gray-700 mb-2">
                Version Notes
                <span class="text-gray-400 font-normal">(optional)</span>
              </label>
              <textarea
                id="notes"
                v-model="publishData.notes"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe what changed in this version..."
              ></textarea>
            </div>

            <!-- Created By -->
            <div>
              <label for="created-by" class="block text-sm font-medium text-gray-700 mb-2">
                Created By
                <span class="text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                id="created-by"
                v-model="publishData.createdBy"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Your name or email"
              />
            </div>

            <!-- Summary -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="text-sm font-medium text-gray-900 mb-3">Publishing Summary</h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Form:</span>
                  <span class="text-gray-900">{{ form.name }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Pages:</span>
                  <span class="text-gray-900">{{ form.pages?.length || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Total Questions:</span>
                  <span class="text-gray-900">{{ totalQuestions }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Next Version:</span>
                  <span class="text-gray-900">{{ nextVersionNumber }}</span>
                </div>
              </div>
            </div>

            <!-- Warning -->
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-yellow-800">Publishing will create a new version</h3>
                  <p class="mt-2 text-sm text-yellow-700">
                    Once published, this version will be live and accessible to form respondents. 
                    Make sure you've tested your form thoroughly.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="modal-footer px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="handlePublish"
            :disabled="isPublishing"
            class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed"
          >
            <span v-if="isPublishing" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Publishing...
            </span>
            <span v-else>Publish Form</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  form: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['publish', 'close'])

// Reactive data
const publishData = ref({
  notes: '',
  createdBy: ''
})
const isPublishing = ref(false)

// Computed properties
const totalQuestions = computed(() => {
  if (!props.form.pages) return 0
  return props.form.pages.reduce((total, page) => {
    return total + (page.questions?.length || 0)
  }, 0)
})

const nextVersionNumber = computed(() => {
  // This would ideally come from the API, but for now we'll estimate
  return (props.form.versions?.length || 0) + 1
})

// Handle publish
const handlePublish = async () => {
  if (isPublishing.value) return
  
  isPublishing.value = true
  
  try {
    await new Promise(resolve => setTimeout(resolve, 500)) // Simulate delay
    emit('publish', publishData.value)
  } catch (error) {
    console.error('Error during publish:', error)
  } finally {
    isPublishing.value = false
  }
}
</script>

<style scoped>
.publish-modal-overlay {
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease-in-out;
}

.publish-modal {
  animation: slideIn 0.3s ease-out;
  max-height: 90vh;
  overflow-y: auto;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-content {
  max-height: calc(90vh - 180px);
  overflow-y: auto;
}

/* Custom scrollbar */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>