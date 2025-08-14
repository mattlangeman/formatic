/**
 * Shared Conditional Logic Composable
 * Eliminates duplication between DynamicForm and FormTableEditor
 */
import { computed } from 'vue'

export function useConditionalLogic() {
  
  /**
   * Evaluate a single condition
   */
  const evaluateCondition = (condition, formData) => {
    const { question_slug, operator, value } = condition
    const fieldValue = formData[question_slug]
    
    switch (operator) {
      case 'equals':
        return fieldValue === value
      case 'not_equals':
        return fieldValue !== value
      case 'contains':
        return fieldValue && fieldValue.toString().includes(value)
      case 'not_contains':
        return !fieldValue || !fieldValue.toString().includes(value)
      case 'is_empty':
        return !fieldValue || fieldValue === ''
      case 'is_not_empty':
        return fieldValue && fieldValue !== ''
      default:
        console.warn(`Unknown condition operator: ${operator}`)
        return false
    }
  }

  /**
   * Evaluate a rule (group of conditions with logical operator)
   */
  const evaluateRule = (rule, formData) => {
    const { conditions, logical_operator } = rule
    
    if (!conditions || conditions.length === 0) {
      return true
    }
    
    const results = conditions.map(condition => evaluateCondition(condition, formData))
    
    if (logical_operator === 'OR') {
      return results.some(result => result)
    } else {
      // Default to AND
      return results.every(result => result)
    }
  }

  /**
   * Evaluate conditional logic for a question
   */
  const evaluateConditionalLogic = (question, formData) => {
    if (!question.conditional_logic || !question.conditional_logic.rules) {
      return {
        visible: true,
        required: question.required || false,
        options: null
      }
    }
    
    const { rules, default_action } = question.conditional_logic
    
    // Find the first matching rule
    for (const rule of rules) {
      if (evaluateRule(rule, formData)) {
        // Apply the actions from the matching rule
        let visible = true
        let required = question.required || false
        let options = null
        
        for (const action of rule.actions) {
          switch (action.type) {
            case 'show':
              visible = true
              break
            case 'hide':
              visible = false
              break
            case 'require':
              required = true
              break
            case 'unrequire':
              required = false
              break
            case 'set_options':
              options = action.options?.en || action.options
              break
            case 'clear_value':
              // This should be handled by the caller
              break
          }
        }
        
        return { visible, required, options }
      }
    }
    
    // No rules matched, apply default action
    if (default_action === 'hide') {
      return {
        visible: false,
        required: false,
        options: null
      }
    }
    
    // Default: show the question as configured
    return {
      visible: true,
      required: question.required || false,
      options: null
    }
  }

  /**
   * Find a specific question by slug in the form structure
   */
  const findQuestionBySlug = (form, questionSlug) => {
    if (!form?.pages) return null
    
    for (const page of form.pages) {
      // Check individual questions
      if (page.questions) {
        const question = page.questions.find(q => q.slug === questionSlug)
        if (question) return question
      }
      
      // Check questions in groups
      if (page.question_groups) {
        for (const group of page.question_groups) {
          if (group.questions) {
            const question = group.questions.find(q => q.slug === questionSlug)
            if (question) return question
          }
        }
      }
    }
    
    return null
  }

  /**
   * Get all visible questions from a page (applying conditional logic)
   */
  const getVisibleQuestions = (page, formData) => {
    const questions = []
    
    // Add individual questions
    if (page.questions) {
      questions.push(...page.questions.filter(question => {
        const logic = evaluateConditionalLogic(question, formData)
        return logic.visible
      }))
    }
    
    // Add questions from question groups
    if (page.question_groups) {
      page.question_groups.forEach(group => {
        if (group.questions) {
          questions.push(...group.questions.filter(question => {
            const logic = evaluateConditionalLogic(question, formData)
            return logic.visible
          }))
        }
      })
    }
    
    return questions
  }

  /**
   * Get dynamic options for a question based on conditional logic
   */
  const getQuestionOptions = (question, formData, questionTypes) => {
    // First check if conditional logic provides dynamic options
    const conditionalLogic = evaluateConditionalLogic(question, formData)
    if (conditionalLogic.options) {
      console.log(`🎯 Using conditional logic options for ${question.slug}:`, conditionalLogic.options)
      return conditionalLogic.options
    }
    
    // Fallback to question type configuration
    const questionType = questionTypes[question.type]
    if (!questionType) {
      console.warn(`⚠️  Question type "${question.type}" not found for options`)
      return []
    }

    // Handle different option formats from Django
    const questionConfig = question.config
    const typeConfig = questionType.config

    // Priority order: question config options > type config options > defaults
    let options = null

    // 1. Check question-specific options first
    if (questionConfig?.options) {
      options = questionConfig.options
    }
    // 2. Check question type default options
    else if (typeConfig?.options) {
      options = typeConfig.options
    }

    if (options) {
      // Use English options by default, fallback to first available language
      const finalOptions = options.en || options[Object.keys(options)[0]] || []
      return finalOptions
    }

    // 3. Handle special cases like yes/no
    if (question.type === 'yes-no') {
      return [
        { label: 'Yes', value: 'yes' },
        { label: 'No', value: 'no' }
      ]
    }

    return []
  }

  /**
   * Get dynamic required state for a question
   */
  const getQuestionRequired = (question, formData) => {
    const conditionalLogic = evaluateConditionalLogic(question, formData)
    return conditionalLogic.required
  }

  /**
   * Get validation rules including conditional logic
   */
  const getValidationRules = (question, formData) => {
    const rules = []
    
    // Check conditional logic for dynamic required state
    const conditionalLogic = evaluateConditionalLogic(question, formData)
    if (conditionalLogic.required) {
      rules.push('required')
    }

    if (question.validation?.email) {
      rules.push('email')
    }

    if (question.validation?.min_length) {
      rules.push(`length:${question.validation.min_length}`)
    }

    if (question.validation?.max_length) {
      rules.push(`length:0,${question.validation.max_length}`)
    }

    return rules.join('|')
  }

  return {
    evaluateCondition,
    evaluateRule,
    evaluateConditionalLogic,
    findQuestionBySlug,
    getVisibleQuestions,
    getQuestionOptions,
    getQuestionRequired,
    getValidationRules
  }
}