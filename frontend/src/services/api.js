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

  // Get published form structure from latest published version
  getForm(slug) {
    return api.get(`/forms/${slug}/`)
  },

  // Get specific form version by version number
  getFormVersion(slug, versionNumber) {
    return api.get(`/forms/${slug}/versions/${versionNumber}/`)
  },

  // Get draft form structure (admin only)
  getDraftForm(slug) {
    return api.get(`/forms/${slug}/draft/`)
  },

  // Create new form version
  createVersion(slug, data) {
    return api.post(`/forms/${slug}/create-version/`, data)
  },

  // Get all versions of a form
  getFormVersions(slug) {
    return api.get(`/forms/${slug}/versions/`)
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
  },

  // Get submission statistics for a form
  getSubmissionStats(formSlug) {
    return api.get(`/submissions/stats/?form_slug=${formSlug}`)
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

// Question Group Templates API methods
export const questionGroupTemplatesApi = {
  // Get all active question group templates
  getTemplates() {
    return api.get('/question-group-templates/')
  },

  // Get specific template by slug
  getTemplate(slug) {
    return api.get(`/question-group-templates/${slug}/`)
  }
}

// Form Builder API methods
export const formBuilderApi = {
  // Form management
  createForm(data) {
    return api.post('/builder/forms/', data)
  },

  getBuilderForm(slug) {
    return api.get(`/builder/forms/${slug}/`)
  },

  updateForm(slug, data) {
    return api.patch(`/builder/forms/${slug}/`, data)
  },

  deleteForm(slug) {
    return api.delete(`/builder/forms/${slug}/`)
  },

  duplicateForm(slug) {
    return api.post(`/builder/forms/${slug}/duplicate/`)
  },

  // Page management
  getPages(formSlug) {
    return api.get(`/builder/forms/${formSlug}/pages/`)
  },

  createPage(formSlug, data) {
    return api.post(`/builder/forms/${formSlug}/pages/`, data)
  },

  updatePage(formSlug, pageId, data) {
    return api.patch(`/builder/forms/${formSlug}/pages/${pageId}/`, data)
  },

  deletePage(formSlug, pageId) {
    return api.delete(`/builder/forms/${formSlug}/pages/${pageId}/`)
  },

  reorderPages(formSlug, pageOrders) {
    return api.post(`/builder/forms/${formSlug}/pages/reorder/`, {
      page_orders: pageOrders
    })
  },

  // Question management
  getQuestions(formSlug, pageId) {
    return api.get(`/builder/forms/${formSlug}/pages/${pageId}/questions/`)
  },

  createQuestion(formSlug, pageId, data) {
    return api.post(`/builder/forms/${formSlug}/pages/${pageId}/questions/`, data)
  },

  updateQuestion(formSlug, pageId, questionId, data) {
    return api.patch(`/builder/forms/${formSlug}/pages/${pageId}/questions/${questionId}/`, data)
  },

  deleteQuestion(formSlug, pageId, questionId) {
    return api.delete(`/builder/forms/${formSlug}/pages/${pageId}/questions/${questionId}/`)
  },

  reorderQuestions(formSlug, pageId, questionOrders) {
    return api.post(`/builder/forms/${formSlug}/pages/${pageId}/questions/reorder/`, {
      question_orders: questionOrders
    })
  },

  // Question Group management
  getQuestionGroups(formSlug, pageId) {
    return api.get(`/builder/forms/${formSlug}/pages/${pageId}/groups/`)
  },

  createQuestionGroup(formSlug, pageId, data) {
    return api.post(`/builder/forms/${formSlug}/pages/${pageId}/groups/`, data)
  },

  updateQuestionGroup(formSlug, pageId, groupId, data) {
    return api.patch(`/builder/forms/${formSlug}/pages/${pageId}/groups/${groupId}/`, data)
  },

  deleteQuestionGroup(formSlug, pageId, groupId) {
    return api.delete(`/builder/forms/${formSlug}/pages/${pageId}/groups/${groupId}/`)
  },

  reorderQuestionGroups(formSlug, pageId, groupOrders) {
    return api.post(`/builder/forms/${formSlug}/pages/${pageId}/groups/reorder/`, {
      group_orders: groupOrders
    })
  },

  // Questions in Groups management
  addQuestionToGroup(formSlug, pageId, groupId, data) {
    return api.post(`/builder/forms/${formSlug}/pages/${pageId}/groups/${groupId}/questions/`, data)
  },

  getGroupedQuestions(formSlug, pageId, groupId) {
    return api.get(`/builder/forms/${formSlug}/pages/${pageId}/groups/${groupId}/questions/`)
  },

  updateGroupedQuestion(formSlug, pageId, groupId, questionId, data) {
    return api.patch(`/builder/forms/${formSlug}/pages/${pageId}/groups/${groupId}/questions/${questionId}/`, data)
  },

  deleteGroupedQuestion(formSlug, pageId, groupId, questionId) {
    return api.delete(`/builder/forms/${formSlug}/pages/${pageId}/groups/${groupId}/questions/${questionId}/`)
  },

  reorderGroupedQuestions(formSlug, pageId, groupId, questionOrders) {
    return api.post(`/builder/forms/${formSlug}/pages/${pageId}/groups/${groupId}/questions/reorder/`, {
      question_orders: questionOrders
    })
  }
}

export default api