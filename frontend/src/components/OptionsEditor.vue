<template>
  <div class="options-editor space-y-4">
    <!-- Header with language tabs -->
    <div class="flex justify-between items-center">
      <label class="block text-xs font-medium text-gray-700">Options</label>
      <div class="flex space-x-1">
        <button
          v-for="lang in supportedLanguages"
          :key="lang.code"
          @click="activeLanguage = lang.code"
          :class="[
            'px-2 py-1 text-xs rounded',
            activeLanguage === lang.code
              ? 'bg-blue-100 text-blue-800'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ lang.name }}
        </button>
      </div>
    </div>

    <!-- Options list for active language -->
    <div class="space-y-2 max-h-60 overflow-y-auto border border-gray-200 rounded-lg p-3">
      <div 
        v-for="(option, index) in currentLanguageOptions" 
        :key="index"
        class="flex items-center space-x-2 group"
      >
        <!-- Drag handle -->
        <div 
          class="drag-handle cursor-move p-1 text-gray-300 group-hover:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity"
          @mousedown="startDrag(index)"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
          </svg>
        </div>

        <!-- Value input (shared across languages) -->
        <div class="flex-1">
          <input
            v-model="option.value"
            @blur="updateOptions"
            @keyup.enter="updateOptions"
            placeholder="value"
            class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            :class="{ 'border-red-300': !option.value && hasValidation }"
          />
        </div>

        <!-- Label input (language specific) -->
        <div class="flex-2">
          <input
            v-model="option.label"
            @blur="updateOptions"
            @keyup.enter="updateOptions"
            :placeholder="`Label (${activeLanguage.toUpperCase()})`"
            class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            :class="{ 'border-red-300': !option.label && hasValidation }"
          />
        </div>

        <!-- Remove button -->
        <button
          @click="removeOption(index)"
          class="p-1 text-red-400 hover:text-red-600 rounded opacity-0 group-hover:opacity-100 transition-opacity"
          :disabled="currentLanguageOptions.length <= 1"
          :class="{ 'cursor-not-allowed opacity-25': currentLanguageOptions.length <= 1 }"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Empty state -->
      <div v-if="currentLanguageOptions.length === 0" class="text-center py-8 text-gray-500 text-sm">
        <svg class="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <p>No options for {{ getSupportedLanguageName(activeLanguage) }}</p>
        <p class="text-xs text-gray-400 mt-1">Add your first option below</p>
      </div>
    </div>

    <!-- Add option button -->
    <button
      @click="addOption"
      class="w-full inline-flex items-center justify-center px-3 py-2 border border-dashed border-gray-300 rounded text-sm text-gray-600 hover:border-gray-400 hover:text-gray-800 hover:bg-gray-50 transition-colors"
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
      </svg>
      Add Option for {{ getSupportedLanguageName(activeLanguage) }}
    </button>

    <!-- Language sync actions -->
    <div class="flex justify-between items-center pt-3 border-t border-gray-200">
      <div class="text-xs text-gray-500">
        {{ getTotalOptionsCount() }} option(s) across {{ Object.keys(localOptions).length }} language(s)
      </div>
      <div class="flex space-x-2">
        <button
          @click="syncFromCurrentLanguage"
          :disabled="Object.keys(localOptions).length <= 1"
          class="px-2 py-1 text-xs bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :title="`Add missing options from ${getSupportedLanguageName(activeLanguage)} to other languages (preserves existing translations)`"
        >
          Sync Structure
        </button>
        <button
          @click="clearAllOptions"
          class="px-2 py-1 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
        >
          Clear All
        </button>
      </div>
    </div>

    <!-- Validation errors -->
    <div v-if="validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-3">
      <div class="flex items-start">
        <svg class="w-4 h-4 text-red-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
        </svg>
        <div class="text-sm">
          <p class="text-red-800 font-medium">Please fix the following issues:</p>
          <ul class="text-red-700 mt-1 list-disc list-inside">
            <li v-for="error in validationErrors" :key="error">{{ error }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  supportedLanguages: {
    type: Array,
    default: () => [
      { code: 'en', name: 'English' },
      { code: 'fr', name: 'French' },
      { code: 'es', name: 'Spanish' }
    ]
  },
  hasValidation: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'validation-change'])

// Reactive data
const activeLanguage = ref(props.supportedLanguages[0]?.code || 'en')
const localOptions = ref({ ...props.modelValue })
const draggedIndex = ref(null)

// Computed properties
const currentLanguageOptions = computed({
  get() {
    return localOptions.value[activeLanguage.value] || []
  },
  set(value) {
    localOptions.value[activeLanguage.value] = value
    updateOptions()
  }
})

const validationErrors = computed(() => {
  const errors = []
  
  // Check each language for validation issues
  Object.entries(localOptions.value).forEach(([lang, options]) => {
    if (!Array.isArray(options)) {
      errors.push(`Invalid options format for ${getSupportedLanguageName(lang)}`)
      return
    }
    
    options.forEach((option, index) => {
      if (!option.value) {
        errors.push(`Option ${index + 1} in ${getSupportedLanguageName(lang)} is missing a value`)
      }
      if (!option.label) {
        errors.push(`Option ${index + 1} in ${getSupportedLanguageName(lang)} is missing a label`)
      }
    })
  })
  
  return errors
})

// Methods
const getSupportedLanguageName = (code) => {
  return props.supportedLanguages.find(lang => lang.code === code)?.name || code.toUpperCase()
}

// Watch for prop changes
watch(() => props.modelValue, (newValue) => {
  localOptions.value = { ...newValue }
}, { deep: true })

watch(validationErrors, (errors) => {
  emit('validation-change', errors.length === 0)
}, { immediate: true })

const getTotalOptionsCount = () => {
  return Object.values(localOptions.value).reduce((total, options) => {
    return total + (Array.isArray(options) ? options.length : 0)
  }, 0)
}

const updateOptions = () => {
  // Clean up empty options while preserving structure
  Object.keys(localOptions.value).forEach(lang => {
    if (Array.isArray(localOptions.value[lang])) {
      // Keep at least one empty option if all are empty
      const hasNonEmptyOptions = localOptions.value[lang].some(opt => opt.value || opt.label)
      if (!hasNonEmptyOptions && localOptions.value[lang].length === 0) {
        localOptions.value[lang] = [{ value: '', label: '' }]
      }
    }
  })
  
  emit('update:modelValue', { ...localOptions.value })
}

const addOption = () => {
  const options = [...currentLanguageOptions.value]
  options.push({ value: '', label: '' })
  currentLanguageOptions.value = options
}

const removeOption = (index) => {
  if (currentLanguageOptions.value.length > 1) {
    const options = [...currentLanguageOptions.value]
    options.splice(index, 1)
    currentLanguageOptions.value = options
  }
}

const syncFromCurrentLanguage = () => {
  const currentOptions = currentLanguageOptions.value
  if (!currentOptions || currentOptions.length === 0) return
  
  // Sync structure while preserving existing translations
  props.supportedLanguages.forEach(lang => {
    if (lang.code !== activeLanguage.value) {
      const existingOptions = localOptions.value[lang.code] || []
      
      // Create a map of existing options by value for quick lookup
      const existingByValue = {}
      existingOptions.forEach(option => {
        if (option.value) {
          existingByValue[option.value] = option.label
        }
      })
      
      // Map current options, preserving existing labels where they exist
      localOptions.value[lang.code] = currentOptions.map(option => ({
        value: option.value,
        // Keep existing label if it exists, otherwise create placeholder
        label: existingByValue[option.value] || 
               option.label || 
               `Label for ${option.value || 'option'}`
      }))
    }
  })
  
  updateOptions()
}

const clearAllOptions = () => {
  if (confirm('Are you sure you want to clear all options for all languages?')) {
    // Reset to single empty option for each language
    props.supportedLanguages.forEach(lang => {
      localOptions.value[lang.code] = [{ value: '', label: '' }]
    })
    updateOptions()
  }
}

// Initialize options if empty
const initializeOptions = () => {
  let needsUpdate = false
  
  props.supportedLanguages.forEach(lang => {
    if (!localOptions.value[lang.code] || !Array.isArray(localOptions.value[lang.code])) {
      localOptions.value[lang.code] = [{ value: '', label: '' }]
      needsUpdate = true
    }
  })
  
  if (needsUpdate) {
    nextTick(() => updateOptions())
  }
}

// Initialize on mount
initializeOptions()

// Drag and drop functionality
const startDrag = (index) => {
  draggedIndex.value = index
}

// Provide a method to focus on a specific option (useful for external validation)
const focusOption = (languageCode, optionIndex, field = 'value') => {
  if (languageCode !== activeLanguage.value) {
    activeLanguage.value = languageCode
  }
  // In a real implementation, you might want to scroll to and focus the specific input
}

// Expose methods for parent components
defineExpose({
  focusOption,
  addOption,
  removeOption,
  syncFromCurrentLanguage,
  clearAllOptions,
  switchToLanguage: (langCode) => { activeLanguage.value = langCode }
})
</script>

<style scoped>
.options-editor {
  font-size: 0.875rem;
}

.flex-2 {
  flex: 2;
}

.drag-handle {
  cursor: move;
}

.drag-handle:hover {
  transform: scale(1.1);
}

input:focus {
  outline: none;
}

/* Custom scrollbar for options list */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>