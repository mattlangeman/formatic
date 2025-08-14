from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

from apps.form_builder.models import DynamicForm, Page, Question, QuestionType


class FormBuilderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create some question types
        self.text_type = QuestionType.objects.create(
            name="Short Text",
            slug="short-text",
            config={"max_length": 255}
        )
        self.number_type = QuestionType.objects.create(
            name="Number",
            slug="number",
            config={"step": 1}
        )
        
        # Create a test form
        self.form = DynamicForm.objects.create(
            name="Test Form",
            slug="test-form"
        )
        
        # Create a test page
        self.page = Page.objects.create(
            form=self.form,
            name="Test Page",
            slug="test-page",
            order=1
        )

    def test_create_form_with_default_page(self):
        """Test creating a form with default page"""
        url = reverse('builder-form-list')
        data = {
            'name': 'New Test Form',
            'slug': 'new-test-form',
            'skip_default_page': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Test Form')
        self.assertEqual(response.data['slug'], 'new-test-form')
        self.assertEqual(len(response.data['pages']), 1)
        self.assertEqual(response.data['pages'][0]['name'], 'Page 1')

    def test_create_form_without_default_page(self):
        """Test creating a form without default page"""
        url = reverse('builder-form-list')
        data = {
            'name': 'Empty Test Form',
            'slug': 'empty-test-form',
            'skip_default_page': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Empty Test Form')
        self.assertEqual(len(response.data['pages']), 0)

    def test_create_form_duplicate_slug(self):
        """Test creating a form with duplicate slug fails"""
        url = reverse('builder-form-list')
        data = {
            'name': 'Another Test Form',
            'slug': 'test-form'  # This slug already exists
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_builder_form(self):
        """Test retrieving a form for the builder"""
        url = reverse('builder-form-detail', kwargs={'slug': self.form.slug})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.form.name)
        self.assertEqual(response.data['slug'], self.form.slug)

    def test_duplicate_form(self):
        """Test duplicating a form"""
        # Add a question to the original form
        Question.objects.create(
            page=self.page,
            type=self.text_type,
            name="Test Question",
            slug="test-question",
            text="What is your name?",
            order=1
        )
        
        url = reverse('builder-form-duplicate', kwargs={'slug': self.form.slug})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Form (Copy)')
        self.assertEqual(response.data['slug'], 'test-form-copy')
        self.assertEqual(len(response.data['pages']), 1)
        self.assertEqual(len(response.data['pages'][0]['questions']), 1)

    def test_create_page(self):
        """Test creating a new page"""
        url = reverse('builder-pages', kwargs={'form_slug': self.form.slug})
        data = {
            'name': 'New Page',
            'slug': 'new-page',
            'config': {},
            'conditional_logic': {}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Page')
        self.assertEqual(response.data['order'], 2)  # Should be after the existing page

    def test_update_page(self):
        """Test updating a page"""
        url = reverse('builder-page-detail', kwargs={
            'form_slug': self.form.slug,
            'pk': self.page.id
        })
        data = {
            'name': 'Updated Page Name',
            'slug': 'updated-page',
            'config': {'theme': 'dark'},
            'conditional_logic': {}
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Page Name')
        self.assertEqual(response.data['config']['theme'], 'dark')

    def test_delete_page(self):
        """Test deleting a page"""
        url = reverse('builder-page-detail', kwargs={
            'form_slug': self.form.slug,
            'pk': self.page.id
        })
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Page.objects.filter(id=self.page.id).exists())

    def test_reorder_pages(self):
        """Test reordering pages"""
        # Create another page
        page2 = Page.objects.create(
            form=self.form,
            name="Page 2",
            slug="page-2",
            order=2
        )
        
        url = reverse('builder-pages-reorder', kwargs={'form_slug': self.form.slug})
        data = {
            'page_orders': [
                {'id': str(page2.id), 'order': 1},
                {'id': str(self.page.id), 'order': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that orders were updated
        self.page.refresh_from_db()
        page2.refresh_from_db()
        self.assertEqual(self.page.order, 2)
        self.assertEqual(page2.order, 1)

    def test_create_question(self):
        """Test creating a new question"""
        url = reverse('builder-questions', kwargs={
            'form_slug': self.form.slug,
            'page_pk': self.page.id
        })
        data = {
            'type_slug': self.text_type.slug,
            'name': 'New Question',
            'slug': 'new-question',
            'text': 'What is your favorite color?',
            'subtext': 'Choose wisely',
            'required': True,
            'config': {'placeholder': 'Enter color...'},
            'validation': {},
            'conditional_logic': {}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Question')
        self.assertEqual(response.data['text'], 'What is your favorite color?')
        self.assertTrue(response.data['required'])
        self.assertEqual(response.data['order'], 1)

    def test_update_question(self):
        """Test updating a question"""
        question = Question.objects.create(
            page=self.page,
            type=self.text_type,
            name="Original Question",
            slug="original-question",
            text="Original text",
            order=1
        )
        
        url = reverse('builder-question-detail', kwargs={
            'form_slug': self.form.slug,
            'page_pk': self.page.id,
            'pk': question.id
        })
        data = {
            'name': 'Updated Question',
            'text': 'Updated question text',
            'required': True,
            'config': {'max_length': 100}
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Question')
        self.assertEqual(response.data['text'], 'Updated question text')
        self.assertTrue(response.data['required'])

    def test_delete_question(self):
        """Test deleting a question"""
        question = Question.objects.create(
            page=self.page,
            type=self.text_type,
            name="Test Question",
            slug="test-question",
            text="Test text",
            order=1
        )
        
        url = reverse('builder-question-detail', kwargs={
            'form_slug': self.form.slug,
            'page_pk': self.page.id,
            'pk': question.id
        })
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=question.id).exists())

    def test_reorder_questions(self):
        """Test reordering questions within a page"""
        question1 = Question.objects.create(
            page=self.page,
            type=self.text_type,
            name="Question 1",
            slug="question-1",
            text="First question",
            order=1
        )
        question2 = Question.objects.create(
            page=self.page,
            type=self.number_type,
            name="Question 2",
            slug="question-2",
            text="Second question",
            order=2
        )
        
        url = reverse('builder-questions-reorder', kwargs={
            'form_slug': self.form.slug,
            'page_pk': self.page.id
        })
        data = {
            'question_orders': [
                {'id': str(question2.id), 'order': 1},
                {'id': str(question1.id), 'order': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that orders were updated
        question1.refresh_from_db()
        question2.refresh_from_db()
        self.assertEqual(question1.order, 2)
        self.assertEqual(question2.order, 1)

    def test_create_question_invalid_type(self):
        """Test creating question with invalid type fails"""
        url = reverse('builder-questions', kwargs={
            'form_slug': self.form.slug,
            'page_pk': self.page.id
        })
        data = {
            'type_slug': 'invalid-type',
            'name': 'Invalid Question',
            'text': 'This should fail'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_question_missing_type(self):
        """Test creating question without type_slug fails"""
        url = reverse('builder-questions', kwargs={
            'form_slug': self.form.slug,
            'page_pk': self.page.id
        })
        data = {
            'name': 'Invalid Question',
            'text': 'This should fail - no type_slug'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type_slug is required', str(response.data))

    def test_form_not_found_error(self):
        """Test accessing non-existent form returns 404"""
        url = reverse('builder-form-detail', kwargs={'slug': 'non-existent'})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_page_not_found_error(self):
        """Test accessing non-existent page returns 404"""
        from uuid import uuid4
        url = reverse('builder-page-detail', kwargs={
            'form_slug': self.form.slug,
            'pk': uuid4()  # Random UUID that doesn't exist
        })
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FormBuilderIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create question types
        self.text_type = QuestionType.objects.create(
            name="Short Text",
            slug="short-text",
            config={"max_length": 255}
        )
        self.dropdown_type = QuestionType.objects.create(
            name="Dropdown",
            slug="dropdown",
            config={
                "multiple": False,
                "options": [
                    {"value": "option1", "label": "Option 1"},
                    {"value": "option2", "label": "Option 2"}
                ]
            }
        )

    def test_complete_form_building_workflow(self):
        """Test a complete form building workflow from start to finish"""
        
        # 1. Create a new form
        form_url = reverse('builder-form-list')
        form_data = {
            'name': 'Complete Test Form',
            'slug': 'complete-test-form',
            'skip_default_page': False
        }
        
        form_response = self.client.post(form_url, form_data, format='json')
        self.assertEqual(form_response.status_code, status.HTTP_201_CREATED)
        
        form_slug = form_response.data['slug']
        page_id = form_response.data['pages'][0]['id']
        
        # 2. Add a second page
        page_url = reverse('builder-pages', kwargs={'form_slug': form_slug})
        page_data = {
            'name': 'Contact Information',
            'slug': 'contact-info',
            'config': {'theme': 'modern'},
            'conditional_logic': {}
        }
        
        page_response = self.client.post(page_url, page_data, format='json')
        self.assertEqual(page_response.status_code, status.HTTP_201_CREATED)
        
        page2_id = page_response.data['id']
        
        # 3. Add questions to the first page
        question_url = reverse('builder-questions', kwargs={
            'form_slug': form_slug,
            'page_pk': page_id
        })
        
        # Add text question
        text_question_data = {
            'type_slug': self.text_type.slug,
            'name': 'Full Name',
            'slug': 'full-name',
            'text': 'What is your full name?',
            'subtext': 'Enter your first and last name',
            'required': True,
            'config': {'placeholder': 'John Doe', 'max_length': 100},
            'validation': {'min_length': 2},
            'conditional_logic': {}
        }
        
        text_response = self.client.post(question_url, text_question_data, format='json')
        self.assertEqual(text_response.status_code, status.HTTP_201_CREATED)
        
        # Add dropdown question
        dropdown_question_data = {
            'type_slug': self.dropdown_type.slug,
            'name': 'Favorite Color',
            'slug': 'favorite-color',
            'text': 'What is your favorite color?',
            'required': False,
            'config': {
                'options': [
                    {'value': 'red', 'label': 'Red'},
                    {'value': 'blue', 'label': 'Blue'},
                    {'value': 'green', 'label': 'Green'}
                ]
            }
        }
        
        dropdown_response = self.client.post(question_url, dropdown_question_data, format='json')
        self.assertEqual(dropdown_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Add questions to the second page
        question2_url = reverse('builder-questions', kwargs={
            'form_slug': form_slug,
            'page_pk': page2_id
        })
        
        email_question_data = {
            'type_slug': self.text_type.slug,
            'name': 'Email Address',
            'slug': 'email-address',
            'text': 'What is your email address?',
            'required': True,
            'config': {'placeholder': 'your@email.com'},
            'validation': {'email': True}
        }
        
        email_response = self.client.post(question2_url, email_question_data, format='json')
        self.assertEqual(email_response.status_code, status.HTTP_201_CREATED)
        
        # 5. Test reordering questions
        reorder_url = reverse('builder-questions-reorder', kwargs={
            'form_slug': form_slug,
            'page_pk': page_id
        })
        
        reorder_data = {
            'question_orders': [
                {'id': dropdown_response.data['id'], 'order': 1},
                {'id': text_response.data['id'], 'order': 2}
            ]
        }
        
        reorder_response = self.client.post(reorder_url, reorder_data, format='json')
        self.assertEqual(reorder_response.status_code, status.HTTP_200_OK)
        
        # 6. Verify final form structure
        final_form_url = reverse('builder-form-detail', kwargs={'slug': form_slug})
        final_response = self.client.get(final_form_url)
        
        self.assertEqual(final_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(final_response.data['pages']), 2)
        
        # Check first page has 2 questions in correct order
        page1 = final_response.data['pages'][0]
        self.assertEqual(len(page1['questions']), 2)
        self.assertEqual(page1['questions'][0]['name'], 'Favorite Color')  # Reordered to first
        self.assertEqual(page1['questions'][1]['name'], 'Full Name')
        
        # Check second page has 1 question
        page2 = final_response.data['pages'][1]
        self.assertEqual(len(page2['questions']), 1)
        self.assertEqual(page2['questions'][0]['name'], 'Email Address')

    def test_form_duplication_preserves_structure(self):
        """Test that form duplication preserves the complete structure"""
        
        # Create original form with complex structure
        form = DynamicForm.objects.create(name="Original Form", slug="original-form")
        
        page1 = Page.objects.create(
            form=form,
            name="Personal Info",
            slug="personal-info",
            order=1,
            config={"theme": "light"}
        )
        
        page2 = Page.objects.create(
            form=form,
            name="Preferences",
            slug="preferences", 
            order=2,
            conditional_logic={"show_if": {"field": "has_account", "value": "yes"}}
        )
        
        # Add questions
        Question.objects.create(
            page=page1,
            type=self.text_type,
            name="First Name",
            slug="first-name",
            text="What's your first name?",
            order=1,
            config={"max_length": 50}
        )
        
        Question.objects.create(
            page=page2,
            type=self.dropdown_type,
            name="Notifications",
            slug="notifications",
            text="How would you like to receive notifications?",
            order=1,
            config={
                "options": [
                    {"value": "email", "label": "Email"},
                    {"value": "sms", "label": "SMS"}
                ]
            }
        )
        
        # Duplicate the form
        duplicate_url = reverse('builder-form-duplicate', kwargs={'slug': form.slug})
        response = self.client.post(duplicate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify structure is preserved
        duplicate_data = response.data
        self.assertEqual(duplicate_data['name'], 'Original Form (Copy)')
        self.assertEqual(len(duplicate_data['pages']), 2)
        
        # Check page 1
        page1_copy = duplicate_data['pages'][0]
        self.assertEqual(page1_copy['name'], 'Personal Info')
        self.assertEqual(page1_copy['config']['theme'], 'light')
        self.assertEqual(len(page1_copy['questions']), 1)
        
        # Check page 2
        page2_copy = duplicate_data['pages'][1]
        self.assertEqual(page2_copy['name'], 'Preferences')
        self.assertEqual(page2_copy['conditional_logic']['show_if']['field'], 'has_account')
        self.assertEqual(len(page2_copy['questions']), 1)
        
        # Check questions are preserved
        question1_copy = page1_copy['questions'][0]
        self.assertEqual(question1_copy['name'], 'First Name')
        self.assertEqual(question1_copy['config']['max_length'], 50)
        
        question2_copy = page2_copy['questions'][0]
        self.assertEqual(question2_copy['name'], 'Notifications')
        self.assertEqual(len(question2_copy['config']['options']), 2)