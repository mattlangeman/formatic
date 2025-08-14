# Frontend Testing Infrastructure

## Overview

This Vue.js application has a comprehensive testing infrastructure including:
- **Unit Tests**: Testing individual functions and utilities
- **Component Tests**: Testing Vue components in isolation
- **Integration Tests**: Testing API service integrations
- **E2E Tests**: Testing complete user workflows with Playwright

## Tech Stack

- **Vitest**: Fast unit test runner built on Vite
- **Vue Test Utils**: Official testing utilities for Vue components
- **Testing Library**: User-centric testing utilities
- **MSW (Mock Service Worker)**: API mocking for integration tests
- **Playwright**: Cross-browser E2E testing
- **GitHub Actions**: CI/CD pipeline for automated testing

## Getting Started

### Installation

```bash
# Install dependencies (if not already installed)
npm install

# Install Playwright browsers for E2E tests
npm run test:e2e:install
```

### Running Tests

```bash
# Run all unit/component tests in watch mode
npm test

# Run tests once (CI mode)
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run all tests
npm run test:all
```

## Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── FormList.vue
│   │   ├── FormList.test.js      # Component test
│   │   ├── DynamicForm.vue
│   │   └── DynamicForm.test.js   # Component test
│   ├── services/
│   │   ├── api.js
│   │   └── api.test.js           # Service test
│   └── tests/
│       ├── setup.js              # Global test setup
│       ├── utils/
│       │   └── test-utils.js     # Test utilities
│       └── mocks/
│           ├── handlers.js       # MSW request handlers
│           └── server.js         # MSW server setup
├── e2e/
│   ├── fixtures/
│   │   └── test-fixtures.js     # Playwright fixtures
│   ├── form-submission.spec.js  # E2E form tests
│   └── form-builder.spec.js     # E2E builder tests
├── vitest.config.js              # Vitest configuration
└── playwright.config.js          # Playwright configuration
```

## Writing Tests

### Component Tests

```javascript
import { describe, it, expect, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/vue'
import { renderWithRouter } from '../tests/utils/test-utils'
import MyComponent from './MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', async () => {
    renderWithRouter(MyComponent, {
      props: { 
        title: 'Test Title' 
      }
    })
    
    await waitFor(() => {
      expect(screen.getByText('Test Title')).toBeInTheDocument()
    })
  })
})
```

### API Service Tests

```javascript
import { describe, it, expect, vi } from 'vitest'
import { myApi } from './api'

vi.mock('axios')

describe('API Service', () => {
  it('fetches data correctly', async () => {
    const mockData = { id: 1, name: 'Test' }
    axios.get = vi.fn().mockResolvedValue({ data: mockData })
    
    const result = await myApi.getData()
    
    expect(result.data).toEqual(mockData)
  })
})
```

### E2E Tests

```javascript
import { test, expect } from '@playwright/test'

test('user can submit form', async ({ page }) => {
  await page.goto('/form/test-form')
  
  await page.fill('input[name="name"]', 'John Doe')
  await page.fill('input[name="email"]', 'john@example.com')
  await page.click('button:has-text("Submit")')
  
  await expect(page).toHaveURL(/success/)
})
```

## Test Utilities

### `renderWithRouter`
Custom render function that includes Vue Router and FormKit configuration.

### `createMockForm` / `createMockSubmission`
Factory functions for creating test data.

### `flushPromises`
Utility to wait for all pending promises to resolve.

### MSW Handlers
Pre-configured API mocks for common endpoints.

## Coverage Requirements

The project aims for:
- **80%** branch coverage
- **80%** function coverage
- **80%** line coverage
- **80%** statement coverage

View coverage report:
```bash
npm run test:coverage
# Open coverage/index.html in browser
```

## CI/CD Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

The CI pipeline includes:
1. Unit/component tests on Node 18.x and 20.x
2. E2E tests with real backend
3. Build verification
4. Lighthouse performance audit
5. Security vulnerability scanning

## Best Practices

### 1. Test User Behavior
Focus on testing what users see and do, not implementation details.

### 2. Use Data Attributes
Add `data-testid` attributes for E2E test selectors:
```vue
<button data-testid="submit-form">Submit</button>
```

### 3. Mock External Dependencies
Use MSW for API mocking to avoid network calls in tests.

### 4. Keep Tests Independent
Each test should be able to run in isolation.

### 5. Use Descriptive Test Names
Test names should clearly describe what is being tested:
```javascript
it('should display validation errors when required fields are empty')
```

### 6. Test Error States
Always test loading, error, and success states.

### 7. Avoid Testing Implementation
Test behavior and outcomes, not how components achieve them.

## Debugging Tests

### Vitest UI
```bash
npm run test:ui
# Opens interactive test UI at http://localhost:51204
```

### Playwright Debug Mode
```bash
# Run with headed browser
npx playwright test --headed

# Debug specific test
npx playwright test form-submission.spec.js --debug
```

### VSCode Integration
Install recommended extensions:
- Vitest extension for inline test running
- Playwright Test for VSCode

## Common Issues

### Issue: Tests fail with "Cannot find module"
**Solution**: Clear cache and reinstall dependencies
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: E2E tests timeout
**Solution**: Increase timeout in playwright.config.js or specific test
```javascript
test.setTimeout(60000) // 60 seconds
```

### Issue: Component not rendering in test
**Solution**: Check if async data is loaded
```javascript
await waitFor(() => {
  expect(screen.getByText('Expected Text')).toBeInTheDocument()
})
```

## Contributing

When adding new features:
1. Write tests first (TDD approach encouraged)
2. Ensure all tests pass locally
3. Add E2E tests for user-facing features
4. Update this documentation if needed

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Library](https://testing-library.com/docs/vue-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)
- [MSW Documentation](https://mswjs.io/)