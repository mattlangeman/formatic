# Testing Guide

This project has comprehensive test coverage (99.27%) with 81 tests covering models, serializers, and API endpoints.

## Quick Start

### Run All Tests
```bash
make test
# or
python test.py
```

### Run Specific Test Categories
```bash
# Model tests only
make test-models
python test.py --models

# API endpoint tests only
make test-api
python test.py --api

# Serializer tests only  
make test-serializers
python test.py --serializers
```

### Run with Coverage Report
```bash
make test-coverage
python test.py --coverage
```

### Run Specific Tests
```bash
# Using Makefile
make test-specific TEST=apps.form_builder.tests.DynamicFormModelTests

# Using test runner
python test.py --specific apps.form_builder.tests.DynamicFormModelTests.test_slug_auto_generation
```

## Test Structure

- **Model Tests** (`form_builder/tests.py`): 33 tests covering all model functionality
  - Slug generation and uniqueness constraints
  - JSON field validation (config, validation, conditional_logic, answers)
  - Model methods and business logic
  - Cascade deletions and relationships

- **Serializer Tests** (`api/test_serializers.py`): 23 tests covering data validation
  - Nested serialization with complex hierarchies
  - JSON field serialization/deserialization
  - Validation logic and error handling

- **API Tests** (`api/tests.py`): 25 tests covering all endpoints
  - Form creation, versioning, and publishing
  - Submission creation and updates
  - Error handling and edge cases
  - Complete workflow integration tests

## Test Infrastructure

- **Factory Boy**: Creates realistic test data with proper JSON field support
- **Django Test Runner**: Reliable, fast test execution
- **Coverage Reports**: Track test coverage with HTML reports
- **Simple Commands**: Easy-to-remember make commands and Python script

## Coverage

Current test coverage: **99.27%**

View detailed coverage:
```bash
make test-coverage
open htmlcov/index.html  # View HTML coverage report
```

## Writing New Tests

### Model Tests
```python
from .factories import DynamicFormFactory

def test_my_model_feature(self):
    form = DynamicFormFactory(name="Test Form")
    # Test your model functionality
    self.assertEqual(form.slug, "test-form")
```

### API Tests
```python
from rest_framework.test import APITestCase
from .factories import APIFormFactory

class MyAPITests(APITestCase):
    def test_my_endpoint(self):
        form = APIFormFactory()
        response = self.client.get(f'/api/forms/{form.slug}/')
        self.assertEqual(response.status_code, 200)
```

### Factory Usage
```python
# Basic usage
form = DynamicFormFactory()
page = PageFactory(form=form, order=1)
question = QuestionFactory(page=page, required=True)

# With custom JSON fields
question = QuestionFactory(
    config={'placeholder': 'Enter value', 'multiline': True},
    validation={'required': True, 'min_length': 5}
)
```

## Debugging Tests

### Verbose Output
```bash
python test.py --verbose
```

### Fail Fast (stop on first error)
```bash
python test.py --fast
```

### Run Single Test
```bash
python test.py --specific apps.form_builder.tests.DynamicFormModelTests.test_slug_auto_generation
```