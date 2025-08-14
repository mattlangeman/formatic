from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

from apps.form_builder.models import DynamicForm, Page, Question, QuestionType, FormVersion


class FormPublishingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create question types
        self.text_type = QuestionType.objects.create(
            name="Short Text",
            slug="short-text",
            config={"max_length": 255}
        )
        
        # Create a test form with structure
        self.form = DynamicForm.objects.create(
            name="Publishing Test Form",
            slug="publishing-test-form"
        )
        
        self.page = Page.objects.create(
            form=self.form,
            name="Test Page",
            slug="test-page",
            order=1
        )
        
        self.question = Question.objects.create(
            page=self.page,
            type=self.text_type,
            name="Test Question",
            slug="test-question",
            text="What is your name?",
            order=1
        )

    def test_create_version_basic(self):
        """Test creating a basic form version"""
        url = reverse('form-create-version', kwargs={'slug': self.form.slug})
        data = {
            'notes': 'Initial version',
            'created_by': 'test@example.com',
            'is_published': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['version_number'], 1)
        self.assertEqual(response.data['notes'], 'Initial version')
        self.assertEqual(response.data['created_by'], 'test@example.com')
        self.assertFalse(response.data['is_published'])
        
        # Verify the version was created in the database
        version = FormVersion.objects.get(form=self.form, version_number=1)
        self.assertIsNotNone(version.serialized_form_data)
        self.assertEqual(version.serialized_form_data['name'], self.form.name)

    def test_create_and_publish_version(self):
        """Test creating and immediately publishing a version"""
        url = reverse('form-create-version', kwargs={'slug': self.form.slug})
        data = {
            'notes': 'Published version',
            'created_by': 'admin@example.com',
            'is_published': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_published'])
        
        # Verify it's the latest published version
        latest_published = self.form.get_latest_published_version()
        self.assertIsNotNone(latest_published)
        self.assertEqual(latest_published.version_number, 1)

    def test_create_multiple_versions(self):
        """Test creating multiple versions increments version numbers"""
        url = reverse('form-create-version', kwargs={'slug': self.form.slug})
        
        # Create first version
        response1 = self.client.post(url, {
            'notes': 'Version 1',
            'is_published': True
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['version_number'], 1)
        
        # Create second version
        response2 = self.client.post(url, {
            'notes': 'Version 2',
            'is_published': False
        }, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['version_number'], 2)

    def test_version_serializes_complete_structure(self):
        """Test that version correctly serializes the complete form structure"""
        url = reverse('form-create-version', kwargs={'slug': self.form.slug})
        data = {'notes': 'Complete structure test'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check the serialized form data
        serialized_data = response.data['serialized_form_data']
        
        # Verify form data
        self.assertEqual(serialized_data['name'], self.form.name)
        self.assertEqual(serialized_data['slug'], self.form.slug)
        self.assertEqual(serialized_data['form_id'], str(self.form.id))
        
        # Verify page data
        self.assertEqual(len(serialized_data['pages']), 1)
        page_data = serialized_data['pages'][0]
        self.assertEqual(page_data['name'], self.page.name)
        self.assertEqual(page_data['slug'], self.page.slug)
        self.assertEqual(page_data['order'], self.page.order)
        
        # Verify question data
        self.assertEqual(len(page_data['questions']), 1)
        question_data = page_data['questions'][0]
        self.assertEqual(question_data['name'], self.question.name)
        self.assertEqual(question_data['text'], self.question.text)
        self.assertEqual(question_data['type'], self.text_type.slug)

    def test_publish_existing_version(self):
        """Test publishing an existing unpublished version"""
        # Create an unpublished version
        version = self.form.create_version(notes='Unpublished version')
        self.assertFalse(version.is_published)
        
        # Publish it
        url = reverse('form-version-publish', kwargs={
            'form_slug': self.form.slug,
            'pk': version.version_number
        })
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_published'])
        
        # Verify in database
        version.refresh_from_db()
        self.assertTrue(version.is_published)

    def test_get_published_form_structure(self):
        """Test retrieving published form structure for rendering"""
        # Create and publish a version
        version = self.form.create_version(notes='For rendering')
        version.is_published = True
        version.save()
        
        # Get the published structure
        url = reverse('form-detail', kwargs={'slug': self.form.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return the serialized form data
        self.assertEqual(response.data['name'], self.form.name)
        self.assertEqual(len(response.data['pages']), 1)

    def test_get_published_form_no_published_version(self):
        """Test getting published form when no published version exists"""
        url = reverse('form-detail', kwargs={'slug': self.form.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No published version available', response.data['error'])

    def test_list_form_versions(self):
        """Test listing all versions of a form"""
        # Create multiple versions
        version1 = self.form.create_version(notes='Version 1', created_by='user1')
        version2 = self.form.create_version(notes='Version 2', created_by='user2')
        version2.is_published = True
        version2.save()
        
        url = reverse('form-versions', kwargs={'form_slug': self.form.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Should be ordered by version number descending
        self.assertEqual(response.data[0]['version_number'], 2)
        self.assertEqual(response.data[1]['version_number'], 1)
        
        # Check version details
        self.assertTrue(response.data[0]['is_published'])
        self.assertFalse(response.data[1]['is_published'])

    def test_get_specific_version(self):
        """Test retrieving a specific version by version number"""
        version = self.form.create_version(notes='Specific version test')
        
        url = reverse('form-version-detail', kwargs={
            'form_slug': self.form.slug,
            'pk': version.version_number
        })
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.form.name)
        self.assertEqual(len(response.data['pages']), 1)


class PublishingWorkflowIntegrationTests(TestCase):
    """Integration tests for the complete publishing workflow"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create question types for testing
        self.text_type = QuestionType.objects.create(
            name="Short Text",
            slug="short-text",
            config={"max_length": 255}
        )
        
        self.dropdown_type = QuestionType.objects.create(
            name="Dropdown",
            slug="dropdown",
            config={"multiple": False}
        )

    def test_complete_build_and_publish_workflow(self):
        """Test the complete workflow: build form -> publish -> retrieve for rendering"""
        
        # 1. Create a form
        form_url = reverse('builder-form-list')
        form_data = {
            'name': 'Complete Workflow Test',
            'slug': 'complete-workflow-test',
            'skip_default_page': True  # Start with empty form
        }
        
        form_response = self.client.post(form_url, form_data, format='json')
        self.assertEqual(form_response.status_code, status.HTTP_201_CREATED)
        form_slug = form_response.data['slug']
        
        # 2. Add a page
        page_url = reverse('builder-pages', kwargs={'form_slug': form_slug})
        page_data = {
            'name': 'User Information',
            'slug': 'user-info',
            'config': {'theme': 'clean'},
            'conditional_logic': {}
        }
        
        page_response = self.client.post(page_url, page_data, format='json')
        self.assertEqual(page_response.status_code, status.HTTP_201_CREATED)
        page_id = page_response.data['id']
        
        # 3. Add questions to the page
        question_url = reverse('builder-questions', kwargs={
            'form_slug': form_slug,
            'page_pk': page_id
        })
        
        # Add name question
        name_question = {
            'type_slug': self.text_type.slug,
            'name': 'Full Name',
            'slug': 'full-name',
            'text': 'What is your full name?',
            'required': True,
            'config': {'placeholder': 'Enter your full name'},
            'validation': {'min_length': 2}
        }
        
        name_response = self.client.post(question_url, name_question, format='json')
        self.assertEqual(name_response.status_code, status.HTTP_201_CREATED)
        
        # Add preferences question
        preferences_question = {
            'type_slug': self.dropdown_type.slug,
            'name': 'Preferences',
            'slug': 'preferences',
            'text': 'What are your preferences?',
            'required': False,
            'config': {
                'options': [
                    {'value': 'option1', 'label': 'Option 1'},
                    {'value': 'option2', 'label': 'Option 2'}
                ]
            }
        }
        
        pref_response = self.client.post(question_url, preferences_question, format='json')
        self.assertEqual(pref_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Create and publish a version
        version_url = reverse('form-create-version', kwargs={'slug': form_slug})
        version_data = {
            'notes': 'Initial public release',
            'created_by': 'form-builder@example.com',
            'is_published': True
        }
        
        version_response = self.client.post(version_url, version_data, format='json')
        self.assertEqual(version_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(version_response.data['version_number'], 1)
        self.assertTrue(version_response.data['is_published'])
        
        # 5. Verify the published form can be retrieved for rendering
        published_url = reverse('form-detail', kwargs={'slug': form_slug})
        published_response = self.client.get(published_url)
        
        self.assertEqual(published_response.status_code, status.HTTP_200_OK)
        published_data = published_response.data
        
        # Verify structure
        self.assertEqual(published_data['name'], 'Complete Workflow Test')
        self.assertEqual(len(published_data['pages']), 1)
        
        page_data = published_data['pages'][0]
        self.assertEqual(page_data['name'], 'User Information')
        self.assertEqual(len(page_data['questions']), 2)
        
        # Verify questions are in the right order
        questions = page_data['questions']
        self.assertEqual(questions[0]['name'], 'Full Name')
        self.assertEqual(questions[1]['name'], 'Preferences')
        
        # 6. Make changes to the form and create a new version
        # Add another question
        email_question = {
            'type_slug': self.text_type.slug,
            'name': 'Email Address',
            'slug': 'email-address',
            'text': 'What is your email address?',
            'required': True,
            'config': {'placeholder': 'your@email.com'},
            'validation': {'email': True}
        }
        
        email_response = self.client.post(question_url, email_question, format='json')
        self.assertEqual(email_response.status_code, status.HTTP_201_CREATED)
        
        # Create version 2
        version2_data = {
            'notes': 'Added email field',
            'created_by': 'form-builder@example.com',
            'is_published': True
        }
        
        version2_response = self.client.post(version_url, version2_data, format='json')
        self.assertEqual(version2_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(version2_response.data['version_number'], 2)
        
        # 7. Verify the new version is now the published one
        final_response = self.client.get(published_url)
        self.assertEqual(final_response.status_code, status.HTTP_200_OK)
        
        # Should now have 3 questions
        final_page = final_response.data['pages'][0]
        self.assertEqual(len(final_page['questions']), 3)
        
        # Verify versions are listed correctly
        versions_url = reverse('form-versions', kwargs={'form_slug': form_slug})
        versions_response = self.client.get(versions_url)
        
        self.assertEqual(versions_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(versions_response.data), 2)
        
        # Both should be published
        self.assertTrue(versions_response.data[0]['is_published'])  # Version 2
        self.assertTrue(versions_response.data[1]['is_published'])  # Version 1