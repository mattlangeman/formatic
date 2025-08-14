import { test as base } from '@playwright/test'

// Custom fixtures for form testing
export const test = base.extend({
  // Fixture to set up a test form
  testForm: async ({ page }, use) => {
    const formData = {
      name: 'E2E Test Form',
      slug: 'e2e-test-form',
      pages: [
        {
          title: 'Personal Information',
          questions: [
            { label: 'Full Name', type: 'text', required: true },
            { label: 'Email', type: 'email', required: true },
            { label: 'Phone', type: 'tel', required: false }
          ]
        },
        {
          title: 'Feedback',
          questions: [
            { label: 'Rating', type: 'radio', required: true },
            { label: 'Comments', type: 'textarea', required: false }
          ]
        }
      ]
    }
    
    await use(formData)
  },

  // Fixture to handle authentication if needed
  authenticatedPage: async ({ page }, use) => {
    // Add authentication logic here if needed
    // For now, just pass through the page
    await use(page)
  },

  // Fixture for API mocking
  mockApi: async ({ page }, use) => {
    // Set up API route mocking
    await page.route('**/api/forms/**', async (route) => {
      const url = route.request().url()
      
      if (url.includes('/api/forms/') && !url.includes('/draft')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            name: 'Test Form',
            slug: 'test-form',
            current_version: {
              pages: [
                {
                  id: 1,
                  title: 'Page 1',
                  questions: []
                }
              ]
            }
          })
        })
      } else {
        await route.continue()
      }
    })
    
    await use(page)
  }
})

export { expect } from '@playwright/test'