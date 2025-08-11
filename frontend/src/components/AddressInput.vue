<template>
  <div class="address-input">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Street Address -->
      <div class="md:col-span-2">
        <FormKit
          type="text"
          :name="`${name}__street`"
          :placeholder="getFieldPlaceholder('street')"
          :validation="getFieldValidation('street')"
          :validation-messages="getFieldValidationMessages('street')"
          :model-value="formData[`${name}__street`] || ''"
          @update:model-value="(value) => updateField(`${name}__street`, value)"
          :actions="false"
        >
          <template #label>
            <span v-html="getFieldFormattedLabel('street')"></span>
          </template>
        </FormKit>
      </div>

      <!-- City -->
      <div>
        <FormKit
          type="text"
          :name="`${name}__city`"
          :placeholder="getFieldPlaceholder('city')"
          :validation="getFieldValidation('city')"
          :validation-messages="getFieldValidationMessages('city')"
          :model-value="formData[`${name}__city`] || ''"
          @update:model-value="(value) => updateField(`${name}__city`, value)"
          :actions="false"
        >
          <template #label>
            <span v-html="getFieldFormattedLabel('city')"></span>
          </template>
        </FormKit>
      </div>

      <!-- State/Province -->
      <div>
        <FormKit
          type="text"
          :name="`${name}__state`"
          :placeholder="getFieldPlaceholder('state')"
          :validation="getFieldValidation('state')"
          :validation-messages="getFieldValidationMessages('state')"
          :model-value="formData[`${name}__state`] || ''"
          @update:model-value="(value) => updateField(`${name}__state`, value)"
          :actions="false"
        >
          <template #label>
            <span v-html="getFieldFormattedLabel('state')"></span>
          </template>
        </FormKit>
      </div>

      <!-- Postal Code -->
      <div>
        <FormKit
          type="text"
          :name="`${name}__postal_code`"
          :placeholder="getFieldPlaceholder('postal_code')"
          :validation="getFieldValidation('postal_code')"
          :validation-messages="getFieldValidationMessages('postal_code')"
          :model-value="formData[`${name}__postal_code`] || ''"
          @update:model-value="(value) => updateField(`${name}__postal_code`, value)"
          :actions="false"
        >
          <template #label>
            <span v-html="getFieldFormattedLabel('postal_code')"></span>
          </template>
        </FormKit>
      </div>

      <!-- Country -->
      <div>
        <FormKit
          type="select"
          :name="`${name}__country`"
          :placeholder="getFieldPlaceholder('country')"
          :validation="getFieldValidation('country')"
          :validation-messages="getFieldValidationMessages('country')"
          :options="getCountryOptions()"
          :model-value="formData[`${name}__country`] || ''"
          @update:model-value="(value) => updateField(`${name}__country`, value)"
          :actions="false"
        >
          <template #label>
            <span v-html="getFieldFormattedLabel('country')"></span>
          </template>
        </FormKit>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'AddressInput',
  props: {
    name: String,
    questionTypeConfig: {
      type: Object,
      default: () => ({})
    },
    formData: {
      type: Object,
      required: true
    },
    updateField: {
      type: Function,
      required: true
    },
    parentRequired: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    console.log('🏠 AddressInput setup - props:', props)
    console.log('🏠 questionTypeConfig:', props.questionTypeConfig)
    
    // Get the address configuration from the question type
    const addressConfig = computed(() => {
      console.log('🏠 Computing addressConfig, questionTypeConfig:', props.questionTypeConfig)
      return props.questionTypeConfig?.fields || {}
    })

    const getFieldLabelText = (fieldName) => {
      const fieldConfig = addressConfig.value[fieldName]
      let label = ''
      
      if (fieldConfig?.label) {
        label = fieldConfig.label.en || fieldConfig.label[Object.keys(fieldConfig.label)[0]] || fieldName
      } else {
        label = fieldName.charAt(0).toUpperCase() + fieldName.slice(1).replace('_', ' ')
      }
      
      return label
    }

    const getFieldFormattedLabel = (fieldName) => {
      const label = getFieldLabelText(fieldName)
      if (isFieldRequired(fieldName)) {
        return `${label} <span style="color: #ef4444; font-weight: normal;">*</span>`
      }
      return label
    }

    const isFieldRequired = (fieldName) => {
      const fieldConfig = addressConfig.value[fieldName]
      // If parent question is required, consider key fields as required
      // Or if the individual field is specifically marked as required
      const isIndividuallyRequired = fieldConfig?.required || false
      const isParentRequired = props.parentRequired && ['street', 'city', 'state', 'postal_code', 'country'].includes(fieldName)
      return isIndividuallyRequired || isParentRequired
    }

    const getFieldPlaceholder = (fieldName) => {
      const fieldConfig = addressConfig.value[fieldName]
      if (fieldConfig?.placeholder) {
        return fieldConfig.placeholder.en || fieldConfig.placeholder[Object.keys(fieldConfig.placeholder)[0]] || ''
      }
      return ''
    }

    const getFieldValidation = (fieldName) => {
      const fieldConfig = addressConfig.value[fieldName]
      const rules = []
      
      if (isFieldRequired(fieldName)) {
        rules.push('required')
      }
      
      return rules.join('|')
    }

    const getFieldValidationMessages = (fieldName) => {
      const fieldLabel = getFieldLabelText(fieldName)
      return {
        required: `${fieldLabel} is required`
      }
    }

    const getCountryOptions = () => {
      const countryOptions = props.questionTypeConfig?.country_options
      console.log('🌍 Country options debug:', countryOptions)
      if (countryOptions?.en) {
        console.log('🌍 Using EN country options:', countryOptions.en)
        return countryOptions.en
      }
      if (countryOptions && Object.keys(countryOptions).length > 0) {
        const firstLang = Object.keys(countryOptions)[0]
        console.log(`🌍 Using ${firstLang} country options:`, countryOptions[firstLang])
        return countryOptions[firstLang]
      }
      console.log('🌍 No country options found, returning empty')
      return []
    }

    return {
      formData: props.formData,
      updateField: props.updateField,
      getFieldLabelText,
      getFieldFormattedLabel,
      isFieldRequired,
      getFieldPlaceholder,
      getFieldValidation,
      getFieldValidationMessages,
      getCountryOptions
    }
  }
}
</script>

<style scoped>
.address-input {
  padding: 1rem 0;
}

.grid {
  gap: 1rem;
}
</style>