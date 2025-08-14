/**
 * Address Field Utility
 * Handles conditional logic specifically for address fields (state/province)
 */
import { useConditionalLogic } from './useConditionalLogic.js'

export function useAddressField() {
  const { findQuestionBySlug, evaluateConditionalLogic } = useConditionalLogic()

  /**
   * Get the state/province question for an address
   */
  const getStateQuestion = (form) => {
    const result = findQuestionBySlug(form, 'address_state')
    console.log('🔍 getStateQuestion result:', result ? 'Found' : 'Not found')
    if (result) {
      console.log('🔍 State question:', result.slug, result.name, result.type)
    }
    return result
  }

  /**
   * Determine if the state field should be visible
   */
  const getStateFieldVisibility = (form, formData) => {
    const stateQuestion = getStateQuestion(form)
    if (!stateQuestion) return true // Default to visible if no state question found
    
    const logic = evaluateConditionalLogic(stateQuestion, formData)
    return logic.visible
  }

  /**
   * Determine if the state field should be required
   */
  const getStateFieldRequired = (form, formData) => {
    const stateQuestion = getStateQuestion(form)
    if (!stateQuestion) return false
    
    const logic = evaluateConditionalLogic(stateQuestion, formData)
    return logic.required
  }

  /**
   * Get the appropriate input type for the state field
   */
  const getStateFieldType = (form, formData) => {
    const stateQuestion = getStateQuestion(form)
    if (!stateQuestion) return 'text'
    
    const logic = evaluateConditionalLogic(stateQuestion, formData)
    return logic.options && logic.options.length > 0 ? 'select' : 'text'
  }

  /**
   * Get the options for the state field (US states, Canadian provinces, etc.)
   */
  const getStateFieldOptions = (form, formData) => {
    console.log('🔍 getStateFieldOptions called')
    console.log('🔍 Form exists:', !!form)
    console.log('🔍 FormData exists:', !!formData)
    console.log('🔍 FormData country:', formData?.address_country)
    
    const stateQuestion = getStateQuestion(form)
    if (!stateQuestion) {
      console.log('🔍 No state question found')
      return []
    }
    
    console.log('🔍 Evaluating conditional logic for state question')
    const logic = evaluateConditionalLogic(stateQuestion, formData)
    console.log('🔍 Conditional logic result:', logic)
    
    const options = logic.options || []
    console.log('🔍 Final options:', options.length, 'options')
    
    return options
  }

  /**
   * Get the appropriate placeholder for the state field
   */
  const getStateFieldPlaceholder = (form, formData) => {
    const stateQuestion = getStateQuestion(form)
    if (!stateQuestion) return 'Enter state or province'
    
    const logic = evaluateConditionalLogic(stateQuestion, formData)
    const country = formData['address_country']
    
    if (logic.options && logic.options.length > 0) {
      if (country === 'US') return 'Select a state'
      if (country === 'CA') return 'Select a province'
      return 'Select state/province'
    }
    
    return 'Enter state or province'
  }

  /**
   * Handle automatic clearing of state field when country changes
   */
  const shouldClearStateField = (form, newFormData, oldFormData) => {
    const stateQuestion = getStateQuestion(form)
    if (!stateQuestion) return false
    
    const oldLogic = evaluateConditionalLogic(stateQuestion, oldFormData)
    const newLogic = evaluateConditionalLogic(stateQuestion, newFormData)
    
    // Clear if field becomes invisible or if country changed
    const countryChanged = oldFormData['address_country'] !== newFormData['address_country']
    const becameInvisible = oldLogic.visible && !newLogic.visible
    
    return becameInvisible || countryChanged
  }

  return {
    getStateQuestion,
    getStateFieldVisibility,
    getStateFieldRequired,
    getStateFieldType,
    getStateFieldOptions,
    getStateFieldPlaceholder,
    shouldClearStateField
  }
}