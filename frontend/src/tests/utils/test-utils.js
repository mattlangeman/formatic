import { render } from '@testing-library/vue'
import { createRouter, createMemoryHistory } from 'vue-router'
import router from '../../router'
import { plugin as FormKitPlugin, defaultConfig } from '@formkit/vue'

// Custom render function that includes router and FormKit
export function renderWithRouter(component, options = {}) {
  // Create a fresh router instance for testing
  const testRouter = createRouter({
    history: createMemoryHistory(),
    routes: router.options.routes,
  })

  const mergedOptions = {
    ...options,
    global: {
      plugins: [
        [FormKitPlugin, defaultConfig],
        testRouter,
        ...(options.global?.plugins || [])
      ],
      stubs: {
        teleport: true,
        ...options.global?.stubs
      },
      ...options.global
    }
  }

  return {
    ...render(component, mergedOptions),
    router: testRouter
  }
}

// Helper to wait for async operations
export function flushPromises() {
  return new Promise((resolve) => {
    setTimeout(resolve, 0)
  })
}

// Helper to create mock API responses
export function createMockResponse(data, status = 200) {
  return Promise.resolve({
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {}
  })
}

// Helper to create mock form data
export function createMockForm(overrides = {}) {
  return {
    id: 1,
    name: 'Test Form',
    slug: 'test-form',
    description: 'Test form description',
    is_active: true,
    current_version: {
      id: 1,
      version_number: 1,
      is_published: true,
      pages: [
        {
          id: 1,
          slug: 'page-1',
          title: 'Page 1',
          order: 1,
          questions: [
            {
              id: 1,
              slug: 'question-1',
              label: 'Test Question',
              help_text: 'This is help text',
              is_required: true,
              order: 1,
              question_type: {
                id: 1,
                slug: 'text',
                name: 'Text Input',
                config: {
                  type: 'text'
                }
              }
            }
          ]
        }
      ]
    },
    ...overrides
  }
}

// Helper to create mock submission
export function createMockSubmission(overrides = {}) {
  return {
    id: 1,
    form: 1,
    status: 'in_progress',
    data: {},
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides
  }
}

// Helper to wait for component updates
export async function waitForUpdates() {
  await flushPromises()
  await new Promise(resolve => setTimeout(resolve, 0))
}