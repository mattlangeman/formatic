# Formatic - Dynamic Form Builder

A powerful, versioned dynamic form system built with Django REST Framework and designed for Vue.js frontend integration. Create complex, multi-page forms with conditional logic, validation, and version control.

## 🚀 Features

- **Dynamic Form Creation**: Build forms with multiple question types (text, email, select, address, etc.)
- **Version Control**: Create, publish, and manage form versions with complete change tracking
- **Multi-page Forms**: Organize questions across multiple pages with conditional navigation
- **Complex Question Types**: Support for composite fields like addresses with multiple sub-fields
- **Conditional Logic**: Show/hide questions and pages based on user responses
- **Submission Management**: Track partial and complete form submissions with auto-save
- **OpenAPI Documentation**: Complete API documentation with interactive Swagger UI
- **Admin Interface**: Rich Django admin for managing forms, versions, and submissions
- **Type Safety**: Full TypeScript support with auto-generated types

## 📋 Quick Start

### Prerequisites
- Python 3.11+
- pipenv

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd formatic

# Install dependencies and set up database
make install

# Load sample question types
make loaddata

# Run the development server
make runserver
```

### Access Points

- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/
- **Alternative Docs**: http://localhost:8000/api/redoc/

## 🏗️ Architecture

### Overview

Formatic follows a decoupled architecture with a Django REST API backend designed to serve Vue.js frontends. The system emphasizes version control, type safety, and flexibility.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue Frontend  │───▶│  Django REST API │───▶│   PostgreSQL    │
│                 │    │                  │    │                 │
│ • Dynamic Forms │    │ • Form Versions  │    │ • Forms Data    │
│ • Type Safety   │    │ • Submissions    │    │ • Submissions   │
│ • Auto-save     │    │ • OpenAPI Schema │    │ • Versions      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 Django Backend

### Core Models

#### `DynamicForm`
The main form container that holds metadata and relationships to pages.

```python
class DynamicForm(models.Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=255)
    slug = SlugField(unique=True)
    is_active = BooleanField(default=True)
```

#### `FormVersion`
Immutable snapshots of form structure, enabling version control and rollback.

```python
class FormVersion(models.Model):
    form = ForeignKey(DynamicForm)
    version_number = PositiveIntegerField()
    serialized_form_data = JSONField()  # Complete form structure
    is_published = BooleanField(default=False)
    notes = TextField(blank=True)
```

#### `Page`
Form pages that group related questions with conditional logic.

```python
class Page(models.Model):
    form = ForeignKey(DynamicForm)
    name = CharField(max_length=255)
    order = IntegerField()
    conditional_logic = JSONField(default=dict)
    config = JSONField(default=dict)
```

#### `Question`
Individual form questions with rich configuration and validation.

```python
class Question(models.Model):
    page = ForeignKey(Page)
    type = ForeignKey(QuestionType)
    text = TextField()
    required = BooleanField(default=False)
    config = JSONField(default=dict)          # Question-specific settings
    validation = JSONField(default=dict)      # Validation rules
    conditional_logic = JSONField(default=dict)  # Show/hide logic
```

#### `QuestionType`
Defines how different question types should be rendered and behave.

```python
class QuestionType(models.Model):
    slug = SlugField(unique=True)  # e.g., 'address', 'rating_scale'
    name = CharField(max_length=100)
    config = JSONField(default=dict)  # Rendering configuration
```

**Example QuestionType configs:**

```python
# Address Type
{
    "fields": [
        {"name": "street", "label": "Street Address", "type": "text", "required": True},
        {"name": "city", "label": "City", "type": "text", "required": True},
        {"name": "state", "label": "State", "type": "select", "required": True},
        {"name": "zip", "label": "ZIP Code", "type": "text", "required": True}
    ],
    "layout": "stacked"
}

# Rating Scale Type
{
    "scale": {"min": 1, "max": 10, "labels": {"1": "Poor", "10": "Excellent"}},
    "display": "horizontal"
}
```

### API Endpoints

#### Forms Management
```
GET    /api/forms/                     # List active forms
GET    /api/forms/{slug}/              # Get published form structure
GET    /api/forms/{slug}/draft/        # Get current draft (admin)
GET    /api/forms/{slug}/versions/     # List form versions
POST   /api/forms/{slug}/create-version/  # Create new version
```

#### Submissions
```
POST   /api/submissions/               # Create new submission
PUT    /api/submissions/{id}/          # Update submission answers
POST   /api/submissions/{id}/complete/ # Mark submission complete
```

#### Documentation
```
GET    /api/schema/                    # OpenAPI JSON schema
GET    /api/docs/                     # Interactive Swagger UI
GET    /api/redoc/                    # Alternative documentation
```

### Serialized Form Structure

When a frontend requests a form, it receives a complete, self-contained structure:

```json
{
  "form_id": "uuid",
  "name": "Customer Survey",
  "slug": "customer-survey",
  "pages": [
    {
      "id": "uuid",
      "name": "Contact Information",
      "order": 1,
      "conditional_logic": {"show_if": {"previous_answer": "yes"}},
      "questions": [
        {
          "id": "uuid",
          "type": {
            "slug": "address",
            "name": "Address",
            "config": {
              "fields": [
                {"name": "street", "label": "Street", "type": "text"}
              ],
              "layout": "stacked"
            }
          },
          "slug": "home_address",
          "text": "What is your home address?",
          "required": true,
          "config": {"show_apartment": true},
          "validation": {"required": true}
        }
      ]
    }
  ]
}
```

### Key Backend Features

#### Version Control System
```python
# Create version from current form structure
version = form.create_version(notes="Added validation", created_by="admin")

# Publish version
version.is_published = True
version.save()

# Get latest published version
published_version = form.get_latest_published_version()
```

#### Auto-save Submissions
```python
# Create submission linked to published version
submission = FormSubmission.objects.create(
    form_version=latest_version,
    user_session_id="session_abc"
)

# Update answers (supports partial updates)
submission.answers.update({"name": "John", "email": "john@example.com"})
submission.save()
```

#### OpenAPI Schema Generation
- Complete type definitions for all JSON fields
- Interactive API documentation
- Auto-generated TypeScript types for frontend
- Example requests/responses for all endpoints

## 🎨 Vue Frontend Integration

### Recommended Architecture

```
src/
├── api/
│   ├── client.ts              # API service layer
│   ├── generated/             # Auto-generated client
│   └── types.ts              # Generated TypeScript types
├── components/
│   ├── DynamicForm.vue       # Main form renderer
│   ├── QuestionRenderer.vue  # Question type router
│   └── questions/            # Question type components
│       ├── TextQuestion.vue
│       ├── AddressQuestion.vue
│       └── RatingQuestion.vue
├── composables/
│   ├── useFormRenderer.ts    # Form loading logic
│   ├── useAutoSave.ts       # Auto-save functionality
│   └── useConditionalLogic.ts # Show/hide logic
└── stores/
    └── forms.ts             # Pinia store
```

### TypeScript Integration

Generate types from your API schema:

```bash
# Generate TypeScript interfaces
npx openapi-typescript http://localhost:8000/api/schema/ -o src/types/api.ts

# Generate full API client
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/api/schema/ \
  -g typescript-axios \
  -o src/api/generated
```

### Dynamic Form Rendering

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <div v-for="page in form.pages" :key="page.id">
      <h2>{{ page.name }}</h2>
      
      <QuestionRenderer
        v-for="question in page.questions"
        :key="question.id"
        :question="question"
        :value="answers[question.slug]"
        @update:value="updateAnswer(question.slug, $event)"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import type { SerializedFormData } from '@/types/api'

// Form structure loaded from API includes QuestionType configs
const form = ref<SerializedFormData | null>(null)

// Answers stored by question slug
const answers = ref<Record<string, any>>({})
</script>
```

### Complex Question Components

Vue components use QuestionType config to render complex fields:

```vue
<!-- AddressQuestion.vue -->
<template>
  <div :class="getLayoutClass()">
    <div v-for="field in question.type.config.fields" :key="field.name">
      <label>{{ field.label }}</label>
      <input 
        v-if="field.type === 'text'"
        v-model="addressData[field.name]"
        :required="field.required"
      />
    </div>
  </div>
</template>

<script setup>
// question.type.config contains the field definitions
// Layout, validation, and rendering rules all come from QuestionType
</script>
```

### Auto-save Implementation

```typescript
// composables/useAutoSave.ts
export function useAutoSave(submissionId: string) {
  const isSaving = ref(false)
  
  const debouncedSave = debounce(async (answers: Record<string, any>) => {
    isSaving.value = true
    try {
      await api.updateSubmission(submissionId, { answers })
    } finally {
      isSaving.value = false
    }
  }, 2000)
  
  return { isSaving, save: debouncedSave }
}
```

## 🧪 Testing

Comprehensive test suite with 99.27% coverage:

```bash
# Run all tests
make test

# Test specific components
make test-models      # Model tests
make test-api         # API endpoint tests  
make test-serializers # Serializer tests

# Coverage report
make test-coverage
```

## 📚 Development Workflow

### Creating Forms

1. **Design Form Structure**: Use Django admin to create forms, pages, and questions
2. **Create Version**: Generate a version snapshot of the current structure
3. **Publish Version**: Mark version as published for frontend consumption
4. **Frontend Integration**: Vue app automatically loads published version

### Form Evolution

1. **Modify Structure**: Update questions, add pages, change validation
2. **Create New Version**: Snapshot changes with notes
3. **Test**: Verify new version works correctly
4. **Publish**: Release new version (old submissions remain linked to their versions)

### Question Type Development

1. **Backend**: Create QuestionType with rendering config
2. **Frontend**: Create Vue component using type config
3. **Register**: Add component to QuestionRenderer mapping
4. **Test**: Verify rendering and data collection

## 🔒 Security Considerations

- UUID primary keys prevent enumeration attacks
- JSON field validation prevents malformed data
- Version immutability ensures data integrity
- Session-based submission tracking
- IP address logging for audit trails

## 📈 Scalability

- Denormalized form versions for fast reads
- JSON fields for flexible schema evolution
- Submission partitioning by form/version
- CDN-friendly static API responses
- Database indexing on slug fields

## 🤝 Contributing

1. Run tests: `make test`
2. Check code style: `make lint`
3. Format code: `make format`
4. Ensure 100% test coverage for new features

## 📄 License

[Your License Here]