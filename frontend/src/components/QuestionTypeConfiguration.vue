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
      <OptionsEditor
        v-model="config.options"
        :has-validation="true"
        @update:model-value="emitUpdate"
      />
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
      <OptionsEditor
        v-model="config.options"
        :has-validation="true"
        @update:model-value="emitUpdate"
      />
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
      
      <!-- Country Options Management -->
      <div>
        <div class="mb-2">
          <label class="block text-xs font-medium text-gray-700 mb-1">Country Options</label>
          <p class="text-xs text-gray-500">Customize the available countries in the dropdown</p>
        </div>
        <OptionsEditor
          v-model="config.country_options"
          :has-validation="false"
          @update:model-value="emitUpdate"
        />
      </div>
    </div>

    <!-- Radio Button Configuration -->
    <div v-else-if="questionType.slug === 'radio' || questionType.slug === 'radio-group'" class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Layout</label>
        <select
          v-model="config.layout"
          @change="emitUpdate"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="vertical">Vertical</option>
          <option value="horizontal">Horizontal</option>
        </select>
      </div>
      
      <!-- Options Management -->
      <OptionsEditor
        v-model="config.options"
        :has-validation="true"
        @update:model-value="emitUpdate"
      />
    </div>

    <!-- Checkbox Configuration -->
    <div v-else-if="questionType.slug === 'checkbox' || questionType.slug === 'checkbox-group'" class="space-y-3">
      <div>
        <label class="flex items-center">
          <input
            v-model="config.allow_other"
            @change="emitUpdate"
            type="checkbox"
            class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
          <span class="ml-2 text-xs text-gray-700">Allow "Other" option with text input</span>
        </label>
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Layout</label>
        <select
          v-model="config.layout"
          @change="emitUpdate"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="vertical">Vertical</option>
          <option value="horizontal">Horizontal</option>
          <option value="grid">Grid (2 columns)</option>
        </select>
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Minimum Selections</label>
        <input
          v-model.number="config.min_selections"
          @blur="emitUpdate"
          type="number"
          min="0"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="0 (no minimum)"
        />
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Maximum Selections</label>
        <input
          v-model.number="config.max_selections"
          @blur="emitUpdate"
          type="number"
          min="1"
          class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="No limit"
        />
      </div>
      
      <!-- Options Management -->
      <OptionsEditor
        v-model="config.options"
        :has-validation="true"
        @update:model-value="emitUpdate"
      />
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
import OptionsEditor from './OptionsEditor.vue'

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

// Options management is now handled by OptionsEditor component

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