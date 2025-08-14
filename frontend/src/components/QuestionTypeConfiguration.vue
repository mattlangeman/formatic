<template>
  <div class="question-type-configuration">
    <!-- Short Text Configuration -->
    <div v-if="questionType.slug === 'short-text'" class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Placeholder Text</label>
        <input
          v-model="config.placeholder"
          @blur="emitUpdate"
          type="text"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Enter placeholder text..."
        />
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Maximum Length</label>
        <input
          v-model.number="config.max_length"
          @blur="emitUpdate"
          type="number"
          min="1"
          max="1000"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>
    </div>

    <!-- Number Configuration -->
    <div v-else-if="questionType.slug === 'number'" class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Placeholder Text</label>
        <input
          v-model="config.placeholder"
          @blur="emitUpdate"
          type="text"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Enter a number..."
        />
      </div>
      
      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Minimum Value</label>
          <input
            v-model.number="config.min"
            @blur="emitUpdate"
            type="number"
            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="No limit"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Maximum Value</label>
          <input
            v-model.number="config.max"
            @blur="emitUpdate"
            type="number"
            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="No limit"
          />
        </div>
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Step Size</label>
        <input
          v-model.number="config.step"
          @blur="emitUpdate"
          type="number"
          min="0.01"
          step="0.01"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Decimal Places</label>
        <select
          v-model.number="config.decimal_places"
          @change="emitUpdate"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option :value="0">Whole numbers only</option>
          <option :value="1">1 decimal place</option>
          <option :value="2">2 decimal places</option>
          <option :value="3">3 decimal places</option>
        </select>
      </div>
    </div>

    <!-- Dropdown Configuration -->
    <div v-else-if="questionType.slug === 'dropdown'" class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Placeholder Text</label>
        <input
          v-model="config.placeholder"
          @blur="emitUpdate"
          type="text"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Select an option..."
        />
      </div>
      
      <div>
        <label class="flex items-center">
          <input
            v-model="config.multiple"
            @change="emitUpdate"
            type="checkbox"
            class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
          <span class="ml-2 text-xs text-gray-700">Allow multiple selections</span>
        </label>
      </div>
      
      <div>
        <label class="flex items-center">
          <input
            v-model="config.searchable"
            @change="emitUpdate"
            type="checkbox"
            class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
          <span class="ml-2 text-xs text-gray-700">Make dropdown searchable</span>
        </label>
      </div>
      
      <!-- Options Management -->
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-2">Options</label>
        <div class="space-y-2 max-h-40 overflow-y-auto">
          <div 
            v-for="(option, index) in dropdownOptions" 
            :key="index"
            class="flex items-center space-x-2"
          >
            <input
              v-model="option.value"
              @blur="emitUpdate"
              placeholder="value"
              class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <input
              v-model="option.label"
              @blur="emitUpdate"
              placeholder="Display label"
              class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              @click="removeOption(index)"
              class="p-1 text-red-400 hover:text-red-600 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        
        <button
          @click="addOption"
          class="mt-2 inline-flex items-center px-2 py-1 border border-dashed border-gray-300 rounded text-xs text-gray-600 hover:border-gray-400 hover:text-gray-800"
        >
          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          Add Option
        </button>
      </div>
    </div>

    <!-- Yes/No Configuration -->
    <div v-else-if="questionType.slug === 'yes-no'" class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Default Value</label>
        <select
          v-model="config.default"
          @change="emitUpdate"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option :value="null">No default</option>
          <option value="yes">Yes</option>
          <option value="no">No</option>
        </select>
      </div>
      
      <!-- Custom Labels -->
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-2">Custom Labels</label>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <input
              v-model="yesNoLabels.yes"
              @blur="updateYesNoLabels"
              placeholder="Yes"
              class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <input
              v-model="yesNoLabels.no"
              @blur="updateYesNoLabels"
              placeholder="No"
              class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Address Configuration -->
    <div v-else-if="questionType.slug === 'address'" class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-2">Required Fields</label>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <label class="flex items-center">
            <input
              v-model="addressFields.street.required"
              @change="updateAddressFields"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 shadow-sm"
            />
            <span class="ml-2">Street Address</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="addressFields.city.required"
              @change="updateAddressFields"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 shadow-sm"
            />
            <span class="ml-2">City</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="addressFields.state.required"
              @change="updateAddressFields"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 shadow-sm"
            />
            <span class="ml-2">State/Province</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="addressFields.postal_code.required"
              @change="updateAddressFields"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 shadow-sm"
            />
            <span class="ml-2">Postal Code</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="addressFields.country.required"
              @change="updateAddressFields"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 shadow-sm"
            />
            <span class="ml-2">Country</span>
          </label>
        </div>
      </div>
      
      <div>
        <label class="flex items-center">
          <input
            v-model="config.geocoding"
            @change="emitUpdate"
            type="checkbox"
            class="rounded border-gray-300 text-blue-600 shadow-sm"
          />
          <span class="ml-2 text-xs text-gray-700">Enable address validation/geocoding</span>
        </label>
      </div>
    </div>

    <!-- Default/Fallback Configuration -->
    <div v-else class="space-y-3">
      <p class="text-xs text-gray-500">
        No specific configuration options available for this question type.
      </p>
      
      <!-- Generic placeholder option -->
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Placeholder Text</label>
        <input
          v-model="config.placeholder"
          @blur="emitUpdate"
          type="text"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Enter placeholder text..."
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  questionType: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['update-config'])

// Reactive data
const config = ref({ ...props.question.config })

// Computed properties for specific configurations
const dropdownOptions = computed({
  get() {
    return config.value.options || [{ value: '', label: '' }]
  },
  set(value) {
    config.value.options = value
    emitUpdate()
  }
})

const yesNoLabels = ref({
  yes: config.value.labels?.yes || 'Yes',
  no: config.value.labels?.no || 'No'
})

const addressFields = ref({
  street: { required: config.value.fields?.street?.required || false },
  city: { required: config.value.fields?.city?.required || false },
  state: { required: config.value.fields?.state?.required || false },
  postal_code: { required: config.value.fields?.postal_code?.required || false },
  country: { required: config.value.fields?.country?.required || false }
})

// Watch for prop changes
watch(() => props.question.config, (newConfig) => {
  config.value = { ...newConfig }
}, { deep: true })

// Emit configuration update
const emitUpdate = () => {
  emit('update-config', config.value)
}

// Dropdown options management
const addOption = () => {
  const options = [...dropdownOptions.value]
  options.push({ value: '', label: '' })
  dropdownOptions.value = options
}

const removeOption = (index) => {
  if (dropdownOptions.value.length > 1) {
    const options = [...dropdownOptions.value]
    options.splice(index, 1)
    dropdownOptions.value = options
  }
}

// Yes/No labels update
const updateYesNoLabels = () => {
  config.value.labels = {
    yes: yesNoLabels.value.yes,
    no: yesNoLabels.value.no
  }
  emitUpdate()
}

// Address fields update
const updateAddressFields = () => {
  config.value.fields = {
    street: { required: addressFields.value.street.required },
    city: { required: addressFields.value.city.required },
    state: { required: addressFields.value.state.required },
    postal_code: { required: addressFields.value.postal_code.required },
    country: { required: addressFields.value.country.required }
  }
  emitUpdate()
}
</script>

<style scoped>
.question-type-configuration {
  font-size: 0.875rem;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
}
</style>