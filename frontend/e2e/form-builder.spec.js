import { test, expect } from './fixtures/test-fixtures'

test.describe('Form Builder', () => {
  test.beforeEach(async ({ page }) => {
    // Mock question types API
    await page.route('**/api/question-types/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, slug: 'text', name: 'Text Input', config: { type: 'text' } },
          { id: 2, slug: 'email', name: 'Email', config: { type: 'email' } },
          { id: 3, slug: 'select', name: 'Dropdown', config: { type: 'select' } },
          { id: 4, slug: 'radio', name: 'Radio Buttons', config: { type: 'radio' } },
          { id: 5, slug: 'checkbox', name: 'Checkboxes', config: { type: 'checkbox' } },
          { id: 6, slug: 'textarea', name: 'Text Area', config: { type: 'textarea' } }
        ])
      })
    })
  })

  test('should create a new form with basic fields', async ({ page }) => {
    await page.goto('/builder/new')
    
    // Fill in form metadata
    await page.fill('input[placeholder*="Form Name"]', 'Employee Survey')
    await page.fill('textarea[placeholder*="Description"]', 'Annual employee satisfaction survey')
    
    // Create the form
    await page.click('button:has-text("Create Form")')
    
    // Should redirect to form builder
    await expect(page).toHaveURL(/\/builder\/employee-survey/)
    
    // Add a page
    await page.click('button:has-text("Add Page")')
    await page.fill('input[placeholder*="Page Title"]', 'Personal Information')
    await page.click('button:has-text("Save Page")')
    
    // Add questions
    await page.click('button:has-text("Add Question")')
    
    // Configure first question
    await page.fill('input[placeholder*="Question Label"]', 'Full Name')
    await page.selectOption('select[name="question-type"]', 'text')
    await page.check('input[type="checkbox"][name="required"]')
    await page.fill('input[placeholder*="Help Text"]', 'Enter your full legal name')
    
    await page.click('button:has-text("Add Question")')
    
    // Verify question was added
    await expect(page.locator('text=Full Name')).toBeVisible()
  })

  test('should edit existing form', async ({ page }) => {
    // Mock existing form data
    await page.route('**/api/form-builder/forms/test-form/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          name: 'Test Form',
          slug: 'test-form',
          description: 'Original description',
          pages: [
            {
              id: 1,
              title: 'Page 1',
              questions: [
                {
                  id: 1,
                  label: 'Existing Question',
                  question_type: { id: 1, slug: 'text' }
                }
              ]
            }
          ]
        })
      })
    })

    await page.goto('/builder/test-form')
    
    // Edit form metadata
    await page.click('button:has-text("Edit Form Settings")')
    await page.fill('input[value="Test Form"]', 'Updated Test Form')
    await page.fill('textarea[value="Original description"]', 'Updated description')
    await page.click('button:has-text("Save Settings")')
    
    // Edit existing question
    await page.click('text=Existing Question')
    await page.fill('input[value="Existing Question"]', 'Updated Question')
    await page.click('button:has-text("Save Question")')
    
    // Verify changes
    await expect(page.locator('text=Updated Question')).toBeVisible()
  })

  test('should reorder questions using drag and drop', async ({ page }) => {
    await page.goto('/builder/test-form')
    
    // Add multiple questions
    for (let i = 1; i <= 3; i++) {
      await page.click('button:has-text("Add Question")')
      await page.fill('input[placeholder*="Question Label"]', `Question ${i}`)
      await page.selectOption('select[name="question-type"]', 'text')
      await page.click('button:has-text("Save")')
    }
    
    // Get drag handles
    const firstQuestion = page.locator('[data-question-id="1"]')
    const thirdQuestion = page.locator('[data-question-id="3"]')
    
    // Drag first question to third position
    await firstQuestion.dragTo(thirdQuestion)
    
    // Verify new order
    const questions = await page.locator('[data-question-id]').allTextContents()
    expect(questions[0]).toContain('Question 2')
    expect(questions[1]).toContain('Question 3')
    expect(questions[2]).toContain('Question 1')
  })

  test('should delete questions and pages', async ({ page }) => {
    await page.goto('/builder/test-form')
    
    // Add a question
    await page.click('button:has-text("Add Question")')
    await page.fill('input[placeholder*="Question Label"]', 'To Be Deleted')
    await page.click('button:has-text("Save")')
    
    // Delete the question
    await page.click('[data-testid="delete-question-1"]')
    await page.click('button:has-text("Confirm Delete")')
    
    // Verify question is removed
    await expect(page.locator('text=To Be Deleted')).not.toBeVisible()
    
    // Add a page
    await page.click('button:has-text("Add Page")')
    await page.fill('input[placeholder*="Page Title"]', 'To Be Deleted Page')
    await page.click('button:has-text("Save Page")')
    
    // Delete the page
    await page.click('[data-testid="delete-page-2"]')
    await page.click('button:has-text("Confirm Delete")')
    
    // Verify page is removed
    await expect(page.locator('text=To Be Deleted Page')).not.toBeVisible()
  })

  test('should configure question with options (radio/select/checkbox)', async ({ page }) => {
    await page.goto('/builder/test-form')
    
    // Add radio button question
    await page.click('button:has-text("Add Question")')
    await page.fill('input[placeholder*="Question Label"]', 'Satisfaction Level')
    await page.selectOption('select[name="question-type"]', 'radio')
    
    // Add options
    await page.click('button:has-text("Add Option")')
    await page.fill('input[placeholder*="Option Label"]', 'Very Satisfied')
    await page.fill('input[placeholder*="Option Value"]', '5')
    
    await page.click('button:has-text("Add Option")')
    await page.fill('input[placeholder*="Option Label"]:nth-of-type(2)', 'Satisfied')
    await page.fill('input[placeholder*="Option Value"]:nth-of-type(2)', '4')
    
    await page.click('button:has-text("Save Question")')
    
    // Verify options are displayed
    await expect(page.locator('text=Very Satisfied')).toBeVisible()
    await expect(page.locator('text=Satisfied')).toBeVisible()
  })

  test('should set up conditional logic', async ({ page }) => {
    await page.goto('/builder/test-form')
    
    // Add trigger question
    await page.click('button:has-text("Add Question")')
    await page.fill('input[placeholder*="Question Label"]', 'Are you employed?')
    await page.selectOption('select[name="question-type"]', 'radio')
    await page.click('button:has-text("Add Option")')
    await page.fill('input[placeholder*="Option Label"]', 'Yes')
    await page.fill('input[placeholder*="Option Value"]', 'yes')
    await page.click('button:has-text("Add Option")')
    await page.fill('input[placeholder*="Option Label"]:nth-of-type(2)', 'No')
    await page.fill('input[placeholder*="Option Value"]:nth-of-type(2)', 'no')
    await page.click('button:has-text("Save Question")')
    
    // Add conditional question
    await page.click('button:has-text("Add Question")')
    await page.fill('input[placeholder*="Question Label"]', 'Company Name')
    await page.selectOption('select[name="question-type"]', 'text')
    
    // Set up conditional logic
    await page.click('button:has-text("Add Condition")')
    await page.selectOption('select[name="condition-field"]', 'are-you-employed')
    await page.selectOption('select[name="condition-operator"]', 'equals')
    await page.fill('input[name="condition-value"]', 'yes')
    
    await page.click('button:has-text("Save Question")')
    
    // Verify conditional logic indicator
    await expect(page.locator('[data-testid="conditional-indicator"]')).toBeVisible()
  })

  test('should preview form', async ({ page }) => {
    await page.goto('/builder/test-form')
    
    // Add some questions first
    await page.click('button:has-text("Add Question")')
    await page.fill('input[placeholder*="Question Label"]', 'Preview Question')
    await page.selectOption('select[name="question-type"]', 'text')
    await page.click('button:has-text("Save")')
    
    // Click preview button
    await page.click('button:has-text("Preview Form")')
    
    // Should open preview in new tab or modal
    const [previewPage] = await Promise.all([
      page.waitForEvent('popup'),
      page.click('button:has-text("Preview")')
    ])
    
    // Verify preview shows the form
    await expect(previewPage.locator('text=Preview Question')).toBeVisible()
    
    // Close preview
    await previewPage.close()
  })

  test('should publish form version', async ({ page }) => {
    await page.goto('/builder/test-form')
    
    // Click publish button
    await page.click('button:has-text("Publish")')
    
    // Confirm publication
    await page.fill('input[placeholder*="Version notes"]', 'Initial release')
    await page.click('button:has-text("Confirm Publish")')
    
    // Should show success message
    await expect(page.locator('text=/published successfully/i')).toBeVisible()
    
    // Version indicator should update
    await expect(page.locator('text=/Version [0-9]+/i')).toBeVisible()
  })

  test('should validate form before publishing', async ({ page }) => {
    await page.goto('/builder/new')
    
    // Create form without any pages/questions
    await page.fill('input[placeholder*="Form Name"]', 'Empty Form')
    await page.click('button:has-text("Create Form")')
    
    // Try to publish
    await page.click('button:has-text("Publish")')
    
    // Should show validation error
    await expect(page.locator('text=/must have at least one page/i')).toBeVisible()
    
    // Add page but no questions
    await page.click('button:has-text("Add Page")')
    await page.fill('input[placeholder*="Page Title"]', 'Empty Page')
    await page.click('button:has-text("Save Page")')
    
    // Try to publish again
    await page.click('button:has-text("Publish")')
    
    // Should show validation error
    await expect(page.locator('text=/must have at least one question/i')).toBeVisible()
  })

  test('should duplicate a question', async ({ page }) => {
    await page.goto('/builder/test-form')
    
    // Add a question
    await page.click('button:has-text("Add Question")')
    await page.fill('input[placeholder*="Question Label"]', 'Original Question')
    await page.fill('input[placeholder*="Help Text"]', 'Original help text')
    await page.check('input[type="checkbox"][name="required"]')
    await page.selectOption('select[name="question-type"]', 'text')
    await page.click('button:has-text("Save")')
    
    // Duplicate the question
    await page.click('[data-testid="duplicate-question-1"]')
    
    // Should create a copy
    await expect(page.locator('text=Original Question (Copy)')).toBeVisible()
    
    // Verify duplicated properties
    const duplicatedQuestion = page.locator('[data-question-label="Original Question (Copy)"]')
    await expect(duplicatedQuestion.locator('text=Original help text')).toBeVisible()
    await expect(duplicatedQuestion.locator('input[type="checkbox"][name="required"]')).toBeChecked()
  })
})