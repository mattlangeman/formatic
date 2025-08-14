import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { renderWithRouter } from '../tests/utils/test-utils'
import FormList from './FormList.vue'
import * as api from '../services/api'

// Mock the API module
vi.mock('../services/api', () => ({
  formApi: {
    getForms: vi.fn()
  },
  submissionApi: {
    createSubmission: vi.fn(),
    getSubmission: vi.fn(),
    updateSubmission: vi.fn()
  }
}))

describe('FormList Component', () => {
  const mockForms = [
    {
      id: 1,
      name: 'Customer Feedback',
      slug: 'customer-feedback',
      description: 'Collect customer feedback',
      is_active: true
    },
    {
      id: 2,
      name: 'Job Application',
      slug: 'job-application',
      description: 'Apply for open positions',
      is_active: true
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    api.formApi.getForms.mockReturnValue(new Promise(() => {}))
    renderWithRouter(FormList)
    
    expect(screen.getByText('Loading forms...')).toBeInTheDocument()
  })

  it('renders forms when loaded successfully', async () => {
    api.formApi.getForms.mockResolvedValue({ data: mockForms })
    renderWithRouter(FormList)

    await waitFor(() => {
      expect(screen.getByText('Customer Feedback')).toBeInTheDocument()
      expect(screen.getByText('Job Application')).toBeInTheDocument()
    })

    expect(screen.getByText('Collect customer feedback')).toBeInTheDocument()
    expect(screen.getByText('Apply for open positions')).toBeInTheDocument()
  })

  it('renders empty state when no forms available', async () => {
    api.formApi.getForms.mockResolvedValue({ data: [] })
    renderWithRouter(FormList)

    await waitFor(() => {
      expect(screen.getByText('No forms available at the moment')).toBeInTheDocument()
    })
  })

  it('renders error state when API call fails', async () => {
    api.formApi.getForms.mockRejectedValue(new Error('Failed to load forms'))
    renderWithRouter(FormList)

    await waitFor(() => {
      expect(screen.getByText('Failed to load forms')).toBeInTheDocument()
      expect(screen.getByText('Try Again')).toBeInTheDocument()
    })
  })

  it('retries loading when Try Again button is clicked', async () => {
    api.formApi.getForms
      .mockRejectedValueOnce(new Error('Failed to load forms'))
      .mockResolvedValueOnce({ data: mockForms })

    renderWithRouter(FormList)
    const user = userEvent.setup()

    await waitFor(() => {
      expect(screen.getByText('Failed to load forms')).toBeInTheDocument()
    })

    await user.click(screen.getByText('Try Again'))

    await waitFor(() => {
      expect(screen.getByText('Customer Feedback')).toBeInTheDocument()
    })
  })

  it('navigates to form detail when clicking on form title', async () => {
    api.formApi.getForms.mockResolvedValue({ data: mockForms })
    const { router } = renderWithRouter(FormList)
    const user = userEvent.setup()

    await waitFor(() => {
      expect(screen.getByText('Customer Feedback')).toBeInTheDocument()
    })

    // Click on the form title link
    const titleLink = screen.getByRole('link', { name: 'Customer Feedback' })
    await user.click(titleLink)

    await waitFor(() => {
      expect(router.currentRoute.value.name).toBe('form-detail')
      expect(router.currentRoute.value.params.slug).toBe('customer-feedback')
    })
  })

  it('shows Create New Form button and navigates correctly', async () => {
    api.formApi.getForms.mockResolvedValue({ data: mockForms })
    const { router } = renderWithRouter(FormList)
    const user = userEvent.setup()

    await waitFor(() => {
      expect(screen.getByText('Create New Form')).toBeInTheDocument()
    })

    await user.click(screen.getByText('Create New Form'))

    await waitFor(() => {
      expect(router.currentRoute.value.name).toBe('new-form')
    })
  })

  it('displays active form status', async () => {
    api.formApi.getForms.mockResolvedValue({ data: mockForms })
    renderWithRouter(FormList)

    await waitFor(() => {
      expect(screen.getByText('Customer Feedback')).toBeInTheDocument()
      expect(screen.getByText('Job Application')).toBeInTheDocument()
    })
    
    // Check that forms show active status
    expect(screen.getAllByText('Active')).toHaveLength(2)
  })
})