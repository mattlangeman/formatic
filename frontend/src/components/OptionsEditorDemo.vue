<template>
  <div class="p-8 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Options Editor Demo</h1>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Options Editor -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h2 class="text-lg font-semibold mb-4">Options Editor</h2>
        
        <OptionsEditor
          v-model="options"
          :has-validation="true"
          @validation-change="validationChanged"
        />
        
        <div class="mt-4 p-3 bg-gray-50 rounded-lg">
          <p class="text-sm font-medium text-gray-700">Validation Status:</p>
          <span :class="[
            'inline-block px-2 py-1 rounded text-xs font-medium mt-1',
            isValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          ]">
            {{ isValid ? 'Valid' : 'Invalid' }}
          </span>
        </div>
      </div>
      
      <!-- JSON Output -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h2 class="text-lg font-semibold mb-4">Generated JSON</h2>
        
        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-auto">
          <pre class="text-sm">{{ JSON.stringify(options, null, 2) }}</pre>
        </div>
        
        <!-- Test buttons -->
        <div class="mt-4 space-x-2">
          <button
            @click="loadSampleData"
            class="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
          >
            Load Sample Data
          </button>
          <button
            @click="clearData"
            class="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
          >
            Clear Data
          </button>
          <button
            @click="exportToClipboard"
            class="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
          >
            Copy JSON
          </button>
          <button
            @click="loadPartialData"
            class="px-3 py-1 bg-yellow-500 text-white rounded text-sm hover:bg-yellow-600"
          >
            Load Partial Data
          </button>
        </div>
        
        <!-- Sync Structure Info -->
        <div class="mt-6 p-3 bg-green-50 rounded-lg">
          <p class="text-sm font-medium text-green-800 mb-2">💡 Sync Structure Tip:</p>
          <p class="text-xs text-green-700 mb-2">Try "Load Partial Data" then use "Sync Structure" in the editor. It will:</p>
          <ul class="text-xs text-green-700 list-disc list-inside space-y-1">
            <li>Preserve existing translations (e.g., "Petit" stays "Petit")</li>
            <li>Add missing options with placeholder labels</li>
            <li>Never overwrite your existing work!</li>
          </ul>
        </div>
        
        <!-- Expected format example -->
        <div class="mt-4 p-3 bg-blue-50 rounded-lg">
          <p class="text-sm font-medium text-blue-800 mb-2">Expected Format:</p>
          <pre class="text-xs text-blue-700 overflow-auto">{{
`{
  "options": {
    "en": [
      {"label": "Option One", "value": "option1"},
      {"label": "Option Two", "value": "option2"}
    ],
    "es": [
      {"label": "Opción 1", "value": "option1"},
      {"label": "Opción 2", "value": "option2"}
    ],
    "fr": [
      {"label": "Option 1", "value": "option1"},
      {"label": "Option 2", "value": "option2"}
    ]
  }
}`
          }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import OptionsEditor from './OptionsEditor.vue'

// Reactive data
const options = ref({
  en: [
    { value: 'option1', label: 'Option One' },
    { value: 'option2', label: 'Option Two' }
  ],
  fr: [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' }
  ],
  es: [
    { value: 'option1', label: 'Opción 1' },
    { value: 'option2', label: 'Opción 2' }
  ]
})

const isValid = ref(true)

// Methods
const validationChanged = (valid) => {
  isValid.value = valid
}

const loadSampleData = () => {
  options.value = {
    en: [
      { value: 'yes', label: 'Yes' },
      { value: 'no', label: 'No' },
      { value: 'maybe', label: 'Maybe' },
      { value: 'unsure', label: 'Not Sure' }
    ],
    fr: [
      { value: 'yes', label: 'Oui' },
      { value: 'no', label: 'Non' }
      // Note: 'maybe' and 'unsure' missing - good for testing sync
    ],
    es: [
      { value: 'yes', label: 'Sí' },
      { value: 'maybe', label: 'Tal vez' }
      // Note: 'no' and 'unsure' missing - good for testing sync
    ]
  }
}

const clearData = () => {
  options.value = {
    en: [{ value: '', label: '' }],
    fr: [{ value: '', label: '' }],
    es: [{ value: '', label: '' }]
  }
}

const exportToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify({ options: options.value }, null, 2))
    alert('JSON copied to clipboard!')
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    alert('Failed to copy to clipboard')
  }
}

const loadPartialData = () => {
  // Load data where some languages are missing options (good for testing sync)
  options.value = {
    en: [
      { value: 'small', label: 'Small' },
      { value: 'medium', label: 'Medium' },
      { value: 'large', label: 'Large' },
      { value: 'xl', label: 'Extra Large' }
    ],
    fr: [
      { value: 'small', label: 'Petit' },
      { value: 'large', label: 'Grand' }
      // missing 'medium' and 'xl' - perfect for sync testing
    ],
    es: [
      { value: 'medium', label: 'Mediano' },
      { value: 'xl', label: 'Extra Grande' }
      // missing 'small' and 'large' - perfect for sync testing
    ]
  }
}
</script>