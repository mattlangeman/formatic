#!/usr/bin/env python
"""
Manual test script to verify the form builder functionality.
Run this with: python manage.py shell < apps/form_builder_api/test_manual.py
"""

from apps.form_builder.models import DynamicForm, Page, Question, QuestionType
from apps.form_builder_api.serializers import *
from django.test import RequestFactory
from rest_framework.test import APIClient
import json

print("🚀 Testing Form Builder Functionality")
print("=" * 50)

# Initialize API client
client = APIClient()

try:
    # 1. Test Question Types
    print("\n📋 Testing Question Types...")
    response = client.get('/api/question-types/')
    if response.status_code == 200:
        question_types = response.data
        print(f"✅ Found {len(question_types)} question types:")
        for qt in question_types:
            print(f"   - {qt['name']} ({qt['slug']})")
    else:
        print(f"❌ Failed to get question types: {response.status_code}")

    # 2. Test Form Creation
    print("\n🏗️  Testing Form Creation...")
    form_data = {
        'name': 'Manual Test Form',
        'slug': 'manual-test-form',
        'skip_default_page': False
    }
    response = client.post('/api/builder/forms/', form_data, format='json')
    if response.status_code == 201:
        form = response.data
        form_slug = form['slug']
        print(f"✅ Created form: {form['name']}")
        print(f"   - Slug: {form_slug}")
        print(f"   - Default pages: {len(form['pages'])}")
    else:
        print(f"❌ Failed to create form: {response.status_code}")
        print(f"   Errors: {response.data}")

    # 3. Test Page Creation
    if response.status_code == 201:
        print("\n📄 Testing Page Creation...")
        page_data = {
            'name': 'Contact Information',
            'slug': 'contact-info',
            'config': {'theme': 'modern'},
            'conditional_logic': {}
        }
        response = client.post(f'/api/builder/forms/{form_slug}/pages/', page_data, format='json')
        if response.status_code == 201:
            page = response.data
            page_id = page['id']
            print(f"✅ Created page: {page['name']}")
            print(f"   - Order: {page['order']}")
        else:
            print(f"❌ Failed to create page: {response.status_code}")
            print(f"   Errors: {response.data}")

    # 4. Test Question Creation
    if 'page_id' in locals():
        print("\n❓ Testing Question Creation...")
        
        # Create a text question
        question_data = {
            'type_slug': 'short-text',
            'name': 'Full Name',
            'slug': 'full-name',
            'text': 'What is your full name?',
            'subtext': 'Please enter your first and last name',
            'required': True,
            'config': {'placeholder': 'John Doe', 'max_length': 100},
            'validation': {'min_length': 2},
            'conditional_logic': {}
        }
        
        response = client.post(f'/api/builder/forms/{form_slug}/pages/{page_id}/questions/', question_data, format='json')
        if response.status_code == 201:
            question = response.data
            print(f"✅ Created question: {question['name']}")
            print(f"   - Type: {question['type']['name']}")
            print(f"   - Required: {question['required']}")
            print(f"   - Order: {question['order']}")
        else:
            print(f"❌ Failed to create question: {response.status_code}")
            print(f"   Errors: {response.data}")

        # Create a dropdown question
        dropdown_data = {
            'type_slug': 'dropdown',
            'name': 'Favorite Color',
            'slug': 'favorite-color',
            'text': 'What is your favorite color?',
            'required': False,
            'config': {
                'options': [
                    {'value': 'red', 'label': 'Red'},
                    {'value': 'blue', 'label': 'Blue'},
                    {'value': 'green', 'label': 'Green'}
                ],
                'placeholder': 'Choose a color...'
            }
        }
        
        response = client.post(f'/api/builder/forms/{form_slug}/pages/{page_id}/questions/', dropdown_data, format='json')
        if response.status_code == 201:
            print(f"✅ Created dropdown question: {response.data['name']}")
        else:
            print(f"❌ Failed to create dropdown question: {response.status_code}")

    # 5. Test Form Publishing
    if 'form_slug' in locals():
        print("\n🚀 Testing Form Publishing...")
        version_data = {
            'notes': 'Manual test version',
            'created_by': 'manual-test@example.com',
            'is_published': True
        }
        
        response = client.post(f'/api/forms/{form_slug}/create-version/', version_data, format='json')
        if response.status_code == 201:
            version = response.data
            print(f"✅ Published version: {version['version_number']}")
            print(f"   - Notes: {version['notes']}")
            print(f"   - Published: {version['is_published']}")
        else:
            print(f"❌ Failed to publish version: {response.status_code}")
            print(f"   Errors: {response.data}")

    # 6. Test Published Form Retrieval
    if 'form_slug' in locals():
        print("\n📖 Testing Published Form Retrieval...")
        response = client.get(f'/api/forms/{form_slug}/')
        if response.status_code == 200:
            published_form = response.data
            print(f"✅ Retrieved published form: {published_form['name']}")
            print(f"   - Pages: {len(published_form['pages'])}")
            if published_form['pages']:
                questions = published_form['pages'][0]['questions']
                print(f"   - Questions in first page: {len(questions)}")
        else:
            print(f"❌ Failed to retrieve published form: {response.status_code}")

    # 7. Test Form Builder Retrieval
    if 'form_slug' in locals():
        print("\n🏗️  Testing Form Builder Retrieval...")
        response = client.get(f'/api/builder/forms/{form_slug}/')
        if response.status_code == 200:
            builder_form = response.data
            print(f"✅ Retrieved builder form: {builder_form['name']}")
            print(f"   - Pages: {len(builder_form['pages'])}")
            if builder_form['pages']:
                page = builder_form['pages'][0]
                print(f"   - Questions in first page: {len(page['questions'])}")
                if page['questions']:
                    for q in page['questions']:
                        print(f"     * {q['name']} ({q['type']['name']})")
        else:
            print(f"❌ Failed to retrieve builder form: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎉 Manual test completed!")
    
    # Summary
    print(f"\n📊 Summary:")
    forms = DynamicForm.objects.all()
    pages = Page.objects.all()
    questions = Question.objects.all()
    question_types = QuestionType.objects.all()
    
    print(f"   - Total Forms: {forms.count()}")
    print(f"   - Total Pages: {pages.count()}")
    print(f"   - Total Questions: {questions.count()}")
    print(f"   - Question Types: {question_types.count()}")

except Exception as e:
    print(f"\n❌ Error during manual test: {e}")
    import traceback
    traceback.print_exc()