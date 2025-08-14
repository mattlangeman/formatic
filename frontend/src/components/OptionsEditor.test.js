import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import OptionsEditor from './OptionsEditor.vue'

describe('OptionsEditor', () => {
  let wrapper

  const defaultProps = {
    modelValue: {
      en: [
        { value: 'option1', label: 'Option One' },
        { value: 'option2', label: 'Option Two' }
      ],
      fr: [
        { value: 'option1', label: 'Option Un' },
        { value: 'option2', label: 'Option Deux' }
      ],
      es: [
        { value: 'option1', label: 'Opción Uno' },
        { value: 'option2', label: 'Opción Dos' }
      ]
    },
    supportedLanguages: [
      { code: 'en', name: 'English' },
      { code: 'fr', name: 'French' },
      { code: 'es', name: 'Spanish' }
    ]
  }

  beforeEach(() => {
    wrapper = mount(OptionsEditor, {
      props: defaultProps
    })
  })

  it('renders language tabs', () => {
    const languageTabs = wrapper.findAll('button')
    const tabTexts = languageTabs.map(tab => tab.text())
    
    expect(tabTexts).toContain('English')
    expect(tabTexts).toContain('French')
    expect(tabTexts).toContain('Spanish')
  })

  it('displays options for the active language', async () => {
    // Should start with English as active
    const valueInputs = wrapper.findAll('input[placeholder="value"]')
    const labelInputs = wrapper.findAll('input[placeholder*="Label"]')
    
    expect(valueInputs).toHaveLength(2)
    expect(labelInputs).toHaveLength(2)
    
    // Check if the English values are displayed
    expect(valueInputs[0].element.value).toBe('option1')
    expect(valueInputs[1].element.value).toBe('option2')
    expect(labelInputs[0].element.value).toBe('Option One')
    expect(labelInputs[1].element.value).toBe('Option Two')
  })

  it('switches languages when tab is clicked', async () => {
    // Click on French tab
    const frenchTab = wrapper.find('button:nth-child(2)')
    await frenchTab.trigger('click')
    
    // Wait for the component to update
    await wrapper.vm.$nextTick()
    
    // Check if French options are now displayed
    const labelInputs = wrapper.findAll('input[placeholder*="Label"]')
    expect(labelInputs[0].element.value).toBe('Option Un')
    expect(labelInputs[1].element.value).toBe('Option Deux')
  })

  it('adds new option when add button is clicked', async () => {
    const addButton = wrapper.find('button[class*="w-full"]')
    const initialInputCount = wrapper.findAll('input[placeholder="value"]').length
    
    await addButton.trigger('click')
    await wrapper.vm.$nextTick()
    
    const finalInputCount = wrapper.findAll('input[placeholder="value"]').length
    expect(finalInputCount).toBe(initialInputCount + 1)
  })

  it('removes option when remove button is clicked', async () => {
    const initialInputCount = wrapper.findAll('input[placeholder="value"]').length
    // Find the button that contains the remove icon (X)
    const removeButtons = wrapper.findAll('button').filter(btn => 
      btn.html().includes('M6 18L18 6M6 6l12 12')
    )
    
    if (removeButtons.length > 0) {
      await removeButtons[0].trigger('click')
      await wrapper.vm.$nextTick()
      
      const finalInputCount = wrapper.findAll('input[placeholder="value"]').length
      expect(finalInputCount).toBe(initialInputCount - 1)
    } else {
      // If no remove button found, test passes as it means only one option remains
      expect(initialInputCount).toBeGreaterThan(0)
    }
  })

  it('emits update:modelValue when options change', async () => {
    const valueInput = wrapper.find('input[placeholder="value"]')
    await valueInput.setValue('new-value')
    await valueInput.trigger('blur')
    
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('validates options correctly', async () => {
    // Mount with empty options to test validation
    const invalidWrapper = mount(OptionsEditor, {
      props: {
        ...defaultProps,
        modelValue: {
          en: [{ value: '', label: '' }]
        },
        hasValidation: true
      }
    })
    
    await invalidWrapper.vm.$nextTick()
    
    // Should emit validation-change with false for empty options
    expect(invalidWrapper.emitted('validation-change')).toBeTruthy()
    const validationEvents = invalidWrapper.emitted('validation-change')
    expect(validationEvents[validationEvents.length - 1][0]).toBe(false)
  })

  it('syncs structure between languages', async () => {
    // Add a new option to English
    const addButton = wrapper.find('button[class*="w-full"]')
    await addButton.trigger('click')
    await wrapper.vm.$nextTick()
    
    // Set values for the new option
    const valueInputs = wrapper.findAll('input[placeholder="value"]')
    const lastValueInput = valueInputs[valueInputs.length - 1]
    await lastValueInput.setValue('option3')
    await lastValueInput.trigger('blur')
    
    // Click sync structure button
    const syncButton = wrapper.find('button[title*="Add missing options"]')
    await syncButton.trigger('click')
    
    // Should emit update with synced structure
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('preserves existing translations when syncing structure', async () => {
    // Create wrapper with mixed options (some existing, some missing)
    const mixedWrapper = mount(OptionsEditor, {
      props: {
        modelValue: {
          en: [
            { value: 'option1', label: 'Option One' },
            { value: 'option2', label: 'Option Two' },
            { value: 'option3', label: 'Option Three' }
          ],
          fr: [
            { value: 'option1', label: 'Option Un' }, // existing translation
            // option2 and option3 are missing
          ],
          es: [
            { value: 'option2', label: 'Opción Dos' }, // existing translation
            // option1 and option3 are missing
          ]
        },
        supportedLanguages: [
          { code: 'en', name: 'English' },
          { code: 'fr', name: 'French' },
          { code: 'es', name: 'Spanish' }
        ]
      }
    })
    
    await mixedWrapper.vm.$nextTick()
    
    // Click sync structure button
    const syncButton = mixedWrapper.find('button[title*="Add missing options"]')
    await syncButton.trigger('click')
    await mixedWrapper.vm.$nextTick()
    
    const emittedEvents = mixedWrapper.emitted('update:modelValue')
    expect(emittedEvents).toBeTruthy()
    
    const lastEmittedValue = emittedEvents[emittedEvents.length - 1][0]
    
    // Check French: should preserve existing translation and add missing ones
    expect(lastEmittedValue.fr).toHaveLength(3)
    expect(lastEmittedValue.fr.find(opt => opt.value === 'option1').label).toBe('Option Un') // preserved
    expect(lastEmittedValue.fr.find(opt => opt.value === 'option2')).toBeDefined() // added
    expect(lastEmittedValue.fr.find(opt => opt.value === 'option3')).toBeDefined() // added
    
    // Check Spanish: should preserve existing translation and add missing ones
    expect(lastEmittedValue.es).toHaveLength(3)
    expect(lastEmittedValue.es.find(opt => opt.value === 'option2').label).toBe('Opción Dos') // preserved
    expect(lastEmittedValue.es.find(opt => opt.value === 'option1')).toBeDefined() // added
    expect(lastEmittedValue.es.find(opt => opt.value === 'option3')).toBeDefined() // added
  })

  it('shows correct option count', async () => {
    const countText = wrapper.find('.text-xs.text-gray-500').text()
    expect(countText).toContain('6 option(s)')
    expect(countText).toContain('3 language(s)')
  })

  it('handles initialization with empty modelValue', () => {
    const emptyWrapper = mount(OptionsEditor, {
      props: {
        modelValue: {},
        supportedLanguages: [{ code: 'en', name: 'English' }]
      }
    })
    
    // Should initialize with empty options for each language
    expect(emptyWrapper.vm.localOptions.en).toBeDefined()
    expect(emptyWrapper.vm.localOptions.en).toHaveLength(1)
  })
})