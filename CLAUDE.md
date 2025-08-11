# Formatic - Claude Code Assistant Configuration

## Project Overview
Formatic is a dynamic form builder built with Django REST Framework. It provides a versioned form system with complex question types, conditional logic, and comprehensive API endpoints for Vue.js frontend integration.

## Quick Start Commands

### Development
```bash
make install          # Install dependencies and migrate database
make runserver         # Start development server on localhost:8000
make shell            # Django shell
```

### Database
```bash
make migrate          # Run migrations
make loaddata         # Load sample question types
make migrate-check    # Check for pending migrations
```

### Testing
```bash
make test             # Run all tests
make test-models      # Run form_builder model tests
make test-api         # Run API endpoint tests
make test-serializers # Run serializer tests
make test-coverage    # Generate coverage report (HTML in htmlcov/)
```

### Code Quality
```bash
make lint             # Check code style with flake8 and black
make format           # Format code with black and isort
```

## Project Structure

- `apps/form_builder/` - Core form models (DynamicForm, Page, Question, QuestionType)
- `apps/api/` - REST API endpoints and serializers
- `formatic_project/` - Django project settings
- `static/` - Static files
- `manage.py` - Django management commands

## Key Models

- **DynamicForm**: Main form container with name, slug, and active status
- **FormVersion**: Immutable snapshots with version control
- **Page**: Form pages with conditional logic and question grouping
- **Question**: Individual form questions with validation and conditional logic
- **QuestionType**: Defines rendering config for different question types

## API Endpoints

- `/api/forms/` - List active forms
- `/api/forms/{slug}/` - Get published form structure
- `/api/forms/{slug}/draft/` - Get current draft (admin)
- `/api/submissions/` - Create and manage form submissions
- `/api/docs/` - Interactive API documentation
- `/admin/` - Django admin interface

## Database
- Uses PostgreSQL
- Migrations located in `apps/*/migrations/`

## Dependencies
- Managed with Pipenv (see Pipfile)
- Python 3.11+
- Django REST Framework
- Development tools: black, flake8, isort, coverage

## Key Feature Implementation Details
- Uses drf-spectacular for schema generation
- Uses django-modeltranslation for multi lingual suport
- Uses JSON fields for configuration option on various model.
  - Must take into account multi-lingual functionality

## Testing
- Django test runner (not pytest despite import statement in test.py)
- 99%+ test coverage requirement
- Factories for test data generation
- Separate test modules for models, API, and serializers

## Vue.js Frontend - FormKit Multi-Page Forms

### Critical Issue: FormKit Data Management with Conditional Fields

**Problem**: FormKit's form-level `v-model` binding overwrites the entire data object when navigating between pages in multi-page forms, removing fields that aren't currently visible in the DOM.

**Symptoms**:
- Initial form load works correctly
- Field values disappear when navigating away and back to a page
- Vue DevTools shows fields becoming `undefined` after navigation
- Data loads correctly in Vue state but doesn't display in FormKit fields

**Root Cause**: FormKit treats the form as a single entity and only maintains data for currently rendered fields. When page navigation hides/shows different fields, FormKit rebuilds its internal data model and loses "hidden" field values.

**Correct Implementation**:
```vue
<!-- WRONG: Form-level binding loses hidden fields -->
<FormKit type="form" v-model="formData">
  <FormKit :name="field.slug" />
</FormKit>

<!-- CORRECT: Individual field bindings preserve all data -->
<FormKit type="form" :actions="false">
  <FormKit 
    :name="field.slug"
    :model-value="formData[field.slug]"
    @update:model-value="(value) => updateField(field.slug, value)"
  />
</FormKit>
```

**Implementation Requirements**:
- Load all form data initially into a Vue reactive object
- Use `:model-value` and `@update:model-value` for individual fields
- Create manual `updateField()` function to manage data updates
- Never use form-level `v-model` with conditionally displayed fields
- This pattern applies to any FormKit implementation where fields are conditionally rendered (pagination, conditional logic, tabs, etc.)