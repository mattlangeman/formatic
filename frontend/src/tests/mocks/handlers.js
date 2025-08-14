import { http, HttpResponse } from 'msw'

const API_BASE = 'http://localhost:8000/api'

// Mock data
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
    description: 'Job application form',
    is_active: true
  }
]

const mockFormDetail = {
  id: 1,
  name: 'Customer Feedback',
  slug: 'customer-feedback',
  description: 'Collect customer feedback',
  is_active: true,
  current_version: {
    id: 1,
    version_number: 1,
    is_published: true,
    pages: [
      {
        id: 1,
        slug: 'personal-info',
        title: 'Personal Information',
        order: 1,
        questions: [
          {
            id: 1,
            slug: 'full-name',
            label: 'Full Name',
            help_text: 'Enter your full name',
            is_required: true,
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
            label: 'Email',
            help_text: 'Enter your email address',
            is_required: true,
            order: 2,
            question_type: {
              id: 2,
              slug: 'email',
              name: 'Email Input',
              config: { type: 'email' }
            }
          }
        ]
      },
      {
        id: 2,
        slug: 'feedback',
        title: 'Your Feedback',
        order: 2,
        questions: [
          {
            id: 3,
            slug: 'rating',
            label: 'Overall Rating',
            help_text: 'Rate your experience',
            is_required: true,
            order: 1,
            question_type: {
              id: 3,
              slug: 'radio',
              name: 'Radio Buttons',
              config: {
                type: 'radio',
                options: [
                  { label: 'Excellent', value: '5' },
                  { label: 'Good', value: '4' },
                  { label: 'Average', value: '3' },
                  { label: 'Poor', value: '2' },
                  { label: 'Very Poor', value: '1' }
                ]
              }
            }
          }
        ]
      }
    ]
  }
}

const mockQuestionTypes = [
  {
    id: 1,
    slug: 'text',
    name: 'Text Input',
    config: { type: 'text' }
  },
  {
    id: 2,
    slug: 'email',
    name: 'Email Input',
    config: { type: 'email' }
  },
  {
    id: 3,
    slug: 'radio',
    name: 'Radio Buttons',
    config: { type: 'radio' }
  },
  {
    id: 4,
    slug: 'checkbox',
    name: 'Checkbox',
    config: { type: 'checkbox' }
  },
  {
    id: 5,
    slug: 'select',
    name: 'Dropdown',
    config: { type: 'select' }
  }
]

const mockSubmission = {
  id: 1,
  form: 1,
  status: 'in_progress',
  data: {},
  created_at: '2024-01-01T12:00:00Z',
  updated_at: '2024-01-01T12:00:00Z'
}

// Request handlers
export const handlers = [
  // Forms endpoints
  http.get(`${API_BASE}/forms/`, () => {
    return HttpResponse.json(mockForms)
  }),

  http.get(`${API_BASE}/forms/:slug/`, ({ params }) => {
    const form = { ...mockFormDetail, slug: params.slug }
    return HttpResponse.json(form)
  }),

  http.get(`${API_BASE}/forms/:slug/draft/`, ({ params }) => {
    const form = { ...mockFormDetail, slug: params.slug }
    return HttpResponse.json(form)
  }),

  // Question types
  http.get(`${API_BASE}/question-types/`, () => {
    return HttpResponse.json(mockQuestionTypes)
  }),

  // Submissions endpoints
  http.post(`${API_BASE}/submissions/`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      ...mockSubmission,
      form: body.form,
      data: body.data || {}
    }, { status: 201 })
  }),

  http.get(`${API_BASE}/submissions/:id/`, ({ params }) => {
    return HttpResponse.json({
      ...mockSubmission,
      id: parseInt(params.id)
    })
  }),

  http.patch(`${API_BASE}/submissions/:id/`, async ({ params, request }) => {
    const body = await request.json()
    return HttpResponse.json({
      ...mockSubmission,
      id: parseInt(params.id),
      data: body.data,
      updated_at: new Date().toISOString()
    })
  }),

  http.put(`${API_BASE}/submissions/:id/`, async ({ params, request }) => {
    const body = await request.json()
    return HttpResponse.json({
      ...mockSubmission,
      id: parseInt(params.id),
      data: body.data,
      status: body.status || 'in_progress',
      updated_at: new Date().toISOString()
    })
  }),

  // Form builder endpoints
  http.post(`${API_BASE}/form-builder/forms/`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      id: 3,
      name: body.name,
      slug: body.slug || body.name.toLowerCase().replace(/\s+/g, '-'),
      description: body.description,
      is_active: true
    }, { status: 201 })
  }),

  http.get(`${API_BASE}/form-builder/forms/:slug/`, ({ params }) => {
    return HttpResponse.json({
      ...mockFormDetail,
      slug: params.slug
    })
  }),

  http.patch(`${API_BASE}/form-builder/forms/:slug/`, async ({ params, request }) => {
    const body = await request.json()
    return HttpResponse.json({
      ...mockFormDetail,
      slug: params.slug,
      ...body
    })
  }),

  // CSRF token endpoint
  http.get(`${API_BASE}/csrf/`, () => {
    return HttpResponse.json({ csrfToken: 'mock-csrf-token' })
  })
]

// Error handlers for testing error scenarios
export const errorHandlers = [
  http.get(`${API_BASE}/forms/`, () => {
    return new HttpResponse(null, { status: 500 })
  }),

  http.get(`${API_BASE}/forms/:slug/`, () => {
    return new HttpResponse(null, { status: 404 })
  }),

  http.post(`${API_BASE}/submissions/`, () => {
    return new HttpResponse(null, { status: 400 })
  })
]