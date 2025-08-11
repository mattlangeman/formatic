import axios from 'axios'

// Store CSRF token
let csrfToken = null

// Create axios instance with default configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  withCredentials: true, // Important for CSRF cookies
  headers: {
    'Content-Type': 'application/json',
  }
})

// Initialize CSRF token
const initializeCsrf = async () => {
  try {
    const response = await api.get('/csrf/')
    csrfToken = response.data.csrfToken
    return csrfToken
  } catch (error) {
    console.error('Failed to get CSRF token:', error)
    return null
  }
}

// Request interceptor to add CSRF token
api.interceptors.request.use(
  async (config) => {
    // Ensure we have a CSRF token for POST, PUT, PATCH, DELETE requests
    if (['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
      if (!csrfToken) {
        await initializeCsrf()
      }
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and CSRF retry
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If CSRF error, try to get new token and retry
    if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
      console.log('CSRF token expired, refreshing...')
      await initializeCsrf()
      
      // Retry the original request with new token
      const originalRequest = error.config
      if (csrfToken && !originalRequest._retry) {
        originalRequest._retry = true
        originalRequest.headers['X-CSRFToken'] = csrfToken
        return api.request(originalRequest)
      }
    }
    
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Initialize CSRF token when module loads
initializeCsrf()

// Form API methods
export const formApi = {
  // Get list of active forms
  getForms() {
    return api.get('/forms/')
  },

  // Get published form structure
  getForm(slug) {
    return api.get(`/forms/${slug}/`)
  },

  // Get draft form structure (admin only)
  getDraftForm(slug) {
    return api.get(`/forms/${slug}/draft/`)
  },

  // Create new form version
  createVersion(slug, data) {
    return api.post(`/forms/${slug}/versions/`, data)
  }
}

// Submission API methods
export const submissionApi = {
  // Create new submission
  createSubmission(data) {
    return api.post('/submissions/', data)
  },

  // Update submission
  updateSubmission(submissionId, data) {
    return api.patch(`/submissions/${submissionId}/`, data)
  },

  // Get submission
  getSubmission(submissionId) {
    return api.get(`/submissions/${submissionId}/`)
  },

  // Get submissions by session ID
  getSubmissionsBySession(sessionId) {
    return api.get(`/submissions/?user_session_id=${sessionId}`)
  },

  // Get submissions by form slug
  getSubmissionsByForm(formSlug) {
    return api.get(`/submissions/?form_slug=${formSlug}`)
  },

  // Submit final answers
  submitForm(submissionId, answers) {
    return api.patch(`/submissions/${submissionId}/`, {
      answers,
      is_complete: true
    })
  }
}

// Question Types API methods
export const questionTypesApi = {
  // Get all question types with their configs
  getQuestionTypes() {
    return api.get('/question-types/')
  },

  // Get specific question type by slug
  getQuestionType(slug) {
    return api.get(`/question-types/${slug}/`)
  }
}

export default api