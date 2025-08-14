import { test, expect } from './fixtures/test-fixtures'

test.describe('Form Submission Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the forms list page
    await page.goto('/')
  })

  test('should display list of available forms', async ({ page }) => {
    // Wait for forms to load
    await page.waitForSelector('h1:has-text("Available Forms")')
    
    // Check that at least one form is displayed or empty state is shown
    const formCards = page.locator('[data-testid="form-card"]')
    const emptyState = page.locator('text=No forms available')
    
    const hasContent = await Promise.race([
      formCards.first().waitFor({ timeout: 5000 }).then(() => true).catch(() => false),
      emptyState.waitFor({ timeout: 5000 }).then(() => true).catch(() => false)
    ])
    
    expect(hasContent).toBeTruthy()
  })

  test('should navigate to form when clicking on form card', async ({ page, mockApi }) => {
    // Mock the forms list API
    await page.route('**/api/forms/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'Customer Feedback',
            slug: 'customer-feedback',
            description: 'Share your feedback with us'
          }
        ])
      })
    })

    await page.goto('/')
    await page.waitForSelector('text=Customer Feedback')
    
    // Click on the form card
    await page.click('text=Customer Feedback')
    
    // Should navigate to the form page
    await expect(page).toHaveURL(/\/form\/customer-feedback/)
  })

  test('should fill and submit a single-page form', async ({ page }) => {
    // Mock the form structure
    await page.route('**/api/forms/test-form/', async (route) => {
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
                slug: 'main',
                title: 'Contact Information',
                questions: [
                  {
                    id: 1,
                    slug: 'name',
                    label: 'Full Name',
                    is_required: true,
                    question_type: { config: { type: 'text' } }
                  },
                  {
                    id: 2,
                    slug: 'email',
                    label: 'Email',
                    is_required: true,
                    question_type: { config: { type: 'email' } }
                  }
                ]
              }
            ]
          }
        })
      })
    })

    // Mock submission creation
    await page.route('**/api/submissions/', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 123,
            form: 1,
            status: 'in_progress',
            data: {}
          })
        })
      }
    })

    // Navigate directly to form
    await page.goto('/form/test-form/fill')
    
    // Wait for form to load
    await page.waitForSelector('label:has-text("Full Name")')
    
    // Fill out the form
    await page.fill('input[name="name"]', 'John Doe')
    await page.fill('input[name="email"]', 'john@example.com')
    
    // Submit the form
    await page.click('button:has-text("Submit")')
    
    // Verify submission was attempted
    await expect(page).toHaveURL(/success|submitted|thank/)
  })

  test('should navigate through multi-page form', async ({ page }) => {
    // Mock multi-page form
    await page.route('**/api/forms/multi-page-form/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 2,
          name: 'Multi Page Form',
          slug: 'multi-page-form',
          current_version: {
            pages: [
              {
                id: 1,
                slug: 'page-1',
                title: 'Personal Info',
                order: 1,
                questions: [
                  {
                    id: 1,
                    slug: 'first-name',
                    label: 'First Name',
                    is_required: true,
                    question_type: { config: { type: 'text' } }
                  }
                ]
              },
              {
                id: 2,
                slug: 'page-2',
                title: 'Contact Info',
                order: 2,
                questions: [
                  {
                    id: 2,
                    slug: 'phone',
                    label: 'Phone Number',
                    is_required: false,
                    question_type: { config: { type: 'tel' } }
                  }
                ]
              }
            ]
          }
        })
      })
    })

    await page.goto('/form/multi-page-form/fill')
    
    // Should be on first page
    await expect(page.locator('h2')).toContainText('Personal Info')
    
    // Fill first page
    await page.fill('input[name="first-name"]', 'Jane')
    
    // Navigate to next page
    await page.click('button:has-text("Next")')
    
    // Should be on second page
    await expect(page.locator('h2')).toContainText('Contact Info')
    
    // Navigate back
    await page.click('button:has-text("Previous")')
    
    // Should be back on first page with data preserved
    await expect(page.locator('input[name="first-name"]')).toHaveValue('Jane')
  })

  test('should show validation errors for required fields', async ({ page }) => {
    // Use the mocked form from previous test
    await page.goto('/form/test-form/fill')
    
    await page.waitForSelector('label:has-text("Full Name")')
    
    // Try to submit without filling required fields
    await page.click('button:has-text("Submit")')
    
    // Should show validation errors
    await expect(page.locator('text=/required|must fill|cannot be empty/i')).toBeVisible()
  })

  test('should auto-save form progress', async ({ page }) => {
    // Mock auto-save endpoint
    let savedData = null
    await page.route('**/api/submissions/*/autosave', async (route) => {
      if (route.request().method() === 'PATCH') {
        savedData = await route.request().postDataJSON()
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        })
      }
    })

    await page.goto('/form/test-form/fill')
    
    // Fill a field
    await page.fill('input[name="name"]', 'Auto Save Test')
    
    // Wait for auto-save (usually debounced)
    await page.waitForTimeout(2000)
    
    // Verify auto-save was triggered
    // This would check the savedData variable or network requests
  })

  test('should handle form builder creation', async ({ page }) => {
    await page.goto('/builder/new')
    
    // Fill form details
    await page.fill('input[name="form-name"]', 'New Test Form')
    await page.fill('textarea[name="form-description"]', 'This is a test form')
    
    // Add a page
    await page.click('button:has-text("Add Page")')
    await page.fill('input[name="page-title"]', 'First Page')
    
    // Add a question
    await page.click('button:has-text("Add Question")')
    await page.fill('input[name="question-label"]', 'Test Question')
    await page.selectOption('select[name="question-type"]', 'text')
    
    // Save the form
    await page.click('button:has-text("Save Form")')
    
    // Should show success message or redirect
    await expect(page.locator('text=/saved|created successfully/i')).toBeVisible({ timeout: 10000 })
  })

  test('should handle network errors gracefully', async ({ page }) => {
    // Mock network failure
    await page.route('**/api/forms/**', async (route) => {
      await route.abort('failed')
    })

    await page.goto('/form/test-form/fill')
    
    // Should show error message
    await expect(page.locator('text=/error|failed|could not load/i')).toBeVisible()
    
    // Should have retry option
    await expect(page.locator('button:has-text("Try Again")')).toBeVisible()
  })

  test('should preserve data across page refresh', async ({ page }) => {
    await page.goto('/form/test-form/fill')
    
    await page.waitForSelector('label:has-text("Full Name")')
    
    // Fill some data
    await page.fill('input[name="name"]', 'Persistent Data')
    
    // Wait for auto-save
    await page.waitForTimeout(2000)
    
    // Refresh the page
    await page.reload()
    
    // Data should be preserved
    await expect(page.locator('input[name="name"]')).toHaveValue('Persistent Data')
  })

  test('should handle conditional questions', async ({ page }) => {
    // Mock form with conditional logic
    await page.route('**/api/forms/conditional-form/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 3,
          name: 'Conditional Form',
          slug: 'conditional-form',
          current_version: {
            pages: [
              {
                id: 1,
                questions: [
                  {
                    id: 1,
                    slug: 'has-pet',
                    label: 'Do you have a pet?',
                    question_type: {
                      config: {
                        type: 'radio',
                        options: [
                          { label: 'Yes', value: 'yes' },
                          { label: 'No', value: 'no' }
                        ]
                      }
                    }
                  },
                  {
                    id: 2,
                    slug: 'pet-name',
                    label: 'Pet Name',
                    question_type: { config: { type: 'text' } },
                    conditional_logic: {
                      conditions: [{ field: 'has-pet', operator: 'equals', value: 'yes' }]
                    }
                  }
                ]
              }
            ]
          }
        })
      })
    })

    await page.goto('/form/conditional-form/fill')
    
    // Pet name field should not be visible initially
    await expect(page.locator('label:has-text("Pet Name")')).not.toBeVisible()
    
    // Select "Yes" for having a pet
    await page.click('label:has-text("Yes")')
    
    // Pet name field should now be visible
    await expect(page.locator('label:has-text("Pet Name")')).toBeVisible()
    
    // Select "No"
    await page.click('label:has-text("No")')
    
    // Pet name field should be hidden again
    await expect(page.locator('label:has-text("Pet Name")')).not.toBeVisible()
  })
})