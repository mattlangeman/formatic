import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { renderWithRouter, flushPromises, createMockForm, createMockSubmission } from '../tests/utils/test-utils'
import DynamicForm from './DynamicForm.vue'
import * as api from '../services/api'

// Mock the API module
vi.mock('../services/api', () => ({
  formApi: {
    getForm: vi.fn()
  },
  questionTypesApi: {
    getQuestionTypes: vi.fn()
  },
  submissionApi: {
    createSubmission: vi.fn(),
    getSubmission: vi.fn(),
    updateSubmission: vi.fn(),
    submitForm: vi.fn()
  }
}))

describe('DynamicForm Component', () => {
  const mockForm = createMockForm({
    pages: [
        {
          id: 1,
          slug: 'page-1',
          name: 'Personal Information',
          order: 1,
          questions: [
            {
              id: 1,
              slug: 'full-name',
              text: 'Full Name',
              subtext: 'Enter your full name',
              required: true,
              order: 1,
              question_type: {
                id: 1,
                slug: 'text',
                name: 'Text Input',
                config: { type: 'text' }
              }
            },
            {
              id: 2,
              slug: 'email',
              text: 'Email Address',
              subtext: 'Enter your email',
              required: true,
              order: 2,
              question_type: {
                id: 2,
                slug: 'email',
                name: 'Email',
                config: { type: 'email' }
              }
            }
          ]
        },
        {
          id: 2,
          slug: 'page-2',
          name: 'Additional Information',
          order: 2,
          questions: [
            {
              id: 3,
              slug: 'comments',
              text: 'Comments',
              subtext: 'Any additional comments',
              required: false,
              order: 1,
              question_type: {
                id: 3,
                slug: 'textarea',
                name: 'Textarea',
                config: { type: 'textarea' }
              }
            }
          ]
        }
      ]
  })

  const mockQuestionTypes = [
    { id: 1, slug: 'text', name: 'Text Input', config: { type: 'text' } },
    { id: 2, slug: 'email', name: 'Email', config: { type: 'email' } },
    { id: 3, slug: 'textarea', name: 'Textarea', config: { type: 'textarea' } }
  ]

  const mockSubmission = createMockSubmission({
    id: 123,
    form: 1,
    data: {}
  })

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default successful API responses
    api.formApi.getForm.mockResolvedValue({ data: mockForm })
    api.questionTypesApi.getQuestionTypes.mockResolvedValue({ data: mockQuestionTypes })
    api.submissionApi.createSubmission.mockResolvedValue({ data: mockSubmission })
    api.submissionApi.getSubmission.mockResolvedValue({ data: mockSubmission })
    api.submissionApi.updateSubmission.mockResolvedValue({ data: mockSubmission })
    api.submissionApi.submitForm.mockResolvedValue({ data: { ...mockSubmission, is_complete: true } })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('loads and displays form with questions', async () => {
    const { router } = renderWithRouter(DynamicForm, {
      props: {
        formSlug: 'test-form'
      }
    })
    
    // Set route params with submission ID
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '123' } })
    
    await waitFor(() => {
      expect(screen.getByText('Personal Information')).toBeInTheDocument()
      expect(screen.getByText('Full Name')).toBeInTheDocument()
      expect(screen.getByText('Email Address')).toBeInTheDocument()
    }, { timeout: 10000 })

    expect(screen.getByText('Enter your full name')).toBeInTheDocument()
  })

  it('creates a new submission when form loads without existing submission ID', async () => {
    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    
    await router.push({ name: 'form', params: { slug: 'test-form' } })
    
    await waitFor(() => {
      expect(api.submissionApi.createSubmission).toHaveBeenCalledWith({
        form_slug: 'test-form'
      })
    })

    // Should redirect to URL with submission ID
    await waitFor(() => {
      expect(router.currentRoute.value.params.submissionId).toBeTruthy()
    }, { timeout: 10000 })
  })

  it('loads existing submission from URL parameters', async () => {
    const existingSubmissionData = {
      ...mockSubmission,
      id: 456,
      answers: { 'full-name': 'John Doe', 'email': 'john@example.com' }
    }

    api.submissionApi.getSubmission.mockResolvedValue({
      data: existingSubmissionData
    })

    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '456' } })

    await waitFor(() => {
      expect(api.submissionApi.getSubmission).toHaveBeenCalledWith('456')
    }, { timeout: 10000 })

    // Verify the component loaded the existing submission
    await waitFor(() => {
      expect(screen.getByText('Test Form')).toBeInTheDocument()
    })
  })

  it('auto-saves form data with debouncing', async () => {
    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '123' } })
    const user = userEvent.setup()

    await waitFor(() => {
      expect(document.querySelector('input[name="full-name"]')).toBeInTheDocument()
    })

    const nameInput = document.querySelector('input[name="full-name"]')
    await user.type(nameInput, 'Jane Smith')

    // Wait for debounced save to trigger
    await waitFor(() => {
      expect(api.submissionApi.updateSubmission).toHaveBeenCalled()
    }, { timeout: 3000 })
  })

  it('navigates between pages in multi-page form', async () => {
    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '123' } })
    const user = userEvent.setup()

    await waitFor(() => {
      expect(screen.getByText('Personal Information')).toBeInTheDocument()
    })

    // Fill out required fields on first page
    const nameInput = document.querySelector('input[name="full-name"]')
    const emailInput = document.querySelector('input[name="email"]')
    await user.type(nameInput, 'John Doe')
    await user.type(emailInput, 'john@example.com')

    // Click Next button
    const nextButton = screen.getByText('Next')
    await user.click(nextButton)

    await waitFor(() => {
      expect(screen.getByText('Additional Information')).toBeInTheDocument()
      expect(document.querySelector('input[name="comments"]')).toBeInTheDocument()
    })

    // Click Previous button
    const prevButton = screen.getByText('Previous')
    await user.click(prevButton)

    await waitFor(() => {
      expect(screen.getByText('Personal Information')).toBeInTheDocument()
    })
  })

  it('validates required fields before submission', async () => {
    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '123' } })
    const user = userEvent.setup()

    await waitFor(() => {
      expect(screen.getByText('Personal Information')).toBeInTheDocument()
    })

    // Try to go to next page without filling required fields
    const nextButton = screen.getByText('Next')
    await user.click(nextButton)

    // Should show validation errors or next button should remain disabled
    await waitFor(() => {
      // Check if validation errors are shown or next button is still disabled
      const nextBtn = screen.getByText('Next')
      expect(nextBtn).toBeInTheDocument()
      // The button should be disabled due to validation
      expect(nextBtn.closest('button')).toBeDisabled()
    })
  })

  it('submits form successfully', async () => {
    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '123' } })
    const user = userEvent.setup()

    // Fill out the form
    await waitFor(() => {
      expect(document.querySelector('input[name="full-name"]')).toBeInTheDocument()
    })

    const nameInput = document.querySelector('input[name="full-name"]')
    const emailInput = document.querySelector('input[name="email"]')
    await user.type(nameInput, 'John Doe')
    await user.type(emailInput, 'john@example.com')

    // Wait a bit for form data to be processed
    await new Promise(resolve => setTimeout(resolve, 100))

    // Go to last page
    await user.click(screen.getByText('Next'))
    
    await waitFor(() => {
      expect(screen.getByText('Additional Information')).toBeInTheDocument()
    })

    // Submit form
    const submitButton = screen.getByText('Submit')
    await user.click(submitButton)

    await waitFor(() => {
      // Check that form was submitted
      expect(api.submissionApi.submitForm).toHaveBeenCalledWith(
        123,
        expect.any(Object)
      )
    })

    // Should show success message
    await waitFor(() => {
      expect(screen.getByText('Form submitted successfully!')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    api.formApi.getForm.mockRejectedValue(new Error('Network error'))

    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '123' } })

    await waitFor(() => {
      expect(screen.getByText(/Failed to load form/i)).toBeInTheDocument()
    })
  })

  it('preserves form data across page navigation', async () => {
    const { router } = renderWithRouter(DynamicForm, { props: { formSlug: 'test-form' } })
    await router.push({ name: 'form-submission', params: { slug: 'test-form', submissionId: '123' } })
    const user = userEvent.setup()

    await waitFor(() => {
      expect(document.querySelector('input[name="full-name"]')).toBeInTheDocument()
    })

    // Enter data on first page
    const nameInput = document.querySelector('input[name="full-name"]')
    const emailInput = document.querySelector('input[name="email"]')
    await user.type(nameInput, 'Jane Doe')
    await user.type(emailInput, 'jane@example.com')

    // Navigate to second page
    await user.click(screen.getByText('Next'))

    await waitFor(() => {
      expect(screen.getByText('Additional Information')).toBeInTheDocument()
    })

    // Navigate back to first page
    await user.click(screen.getByText('Previous'))

    // Data should be preserved
    await waitFor(() => {
      const nameInput = document.querySelector('input[name="full-name"]')
      const emailInput = document.querySelector('input[name="email"]')
      expect(nameInput).toBeInTheDocument()
      expect(nameInput).toHaveValue('Jane Doe')
      expect(emailInput).toHaveValue('jane@example.com')
    })
  })
})