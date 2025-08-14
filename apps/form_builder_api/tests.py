from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from apps.form_builder.models import DynamicForm, FormVersion, FormSubmission
from apps.form_builder.factories import (
    DynamicFormFactory, FormVersionFactory, PageFactory, QuestionFactory,
    FormSubmissionFactory, PublishedFormVersionFactory, QuestionTypeFactory
)
from .factories import APIFormFactory, APIPublishedFormVersionFactory


class FormViewSetTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
    
    def test_list_active_forms(self):
        """Test listing active forms"""
        active_form1 = DynamicFormFactory(is_active=True)
        active_form2 = DynamicFormFactory(is_active=True)
        inactive_form = DynamicFormFactory(is_active=False)
        
        url = reverse('form-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        form_ids = [form['id'] for form in response.data]
        self.assertIn(str(active_form1.id), form_ids)
        self.assertIn(str(active_form2.id), form_ids)
        self.assertNotIn(str(inactive_form.id), form_ids)
    
    def test_retrieve_published_form_version(self):
        """Test retrieving latest published version of a form"""
        form = DynamicFormFactory(slug='test-form')
        
        # Create unpublished version
        unpublished = FormVersionFactory(form=form, version_number=1, is_published=False)
        
        # Create published version
        published = FormVersionFactory(
            form=form,
            version_number=2,
            is_published=True,
            serialized_form_data={'form_id': str(form.id), 'name': form.name, 'pages': []}
        )
        
        url = reverse('form-detail', kwargs={'slug': 'test-form'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['form_id'], str(form.id))
        self.assertEqual(response.data['name'], form.name)
    
    def test_retrieve_form_no_published_version(self):
        """Test retrieving form with no published version returns 404"""
        form = DynamicFormFactory(slug='test-form')
        FormVersionFactory(form=form, is_published=False)
        
        url = reverse('form-detail', kwargs={'slug': 'test-form'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_retrieve_inactive_form_404(self):
        """Test retrieving inactive form returns 404"""
        form = DynamicFormFactory(slug='test-form', is_active=False)
        
        url = reverse('form-detail', kwargs={'slug': 'test-form'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_draft_endpoint(self):
        """Test getting current draft structure"""
        form = DynamicFormFactory(slug='test-form')
        page = PageFactory(form=form)
        question = QuestionFactory(page=page)
        
        url = reverse('form-draft', kwargs={'slug': 'test-form'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(form.id))
        self.assertEqual(len(response.data['pages']), 1)
        self.assertEqual(len(response.data['pages'][0]['questions']), 1)
    
    def test_versions_list(self):
        """Test listing all versions of a form"""
        form = DynamicFormFactory(slug='test-form')
        v1 = FormVersionFactory(form=form, version_number=1)
        v2 = FormVersionFactory(form=form, version_number=2)
        v3 = FormVersionFactory(form=form, version_number=3)
        
        url = reverse('form-versions', kwargs={'slug': 'test-form'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Should be ordered by version number descending
        version_numbers = [v['version_number'] for v in response.data]
        self.assertEqual(version_numbers, [3, 2, 1])
    
    def test_create_version_basic(self):
        """Test creating a new version"""
        form = DynamicFormFactory(slug='test-form')
        page = PageFactory(form=form, order=1)
        question = QuestionFactory(page=page, order=1)
        
        url = reverse('form-create-version', kwargs={'slug': 'test-form'})
        data = {
            'notes': 'Test version',
            'created_by': 'admin',
            'is_published': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['version_number'], 1)
        self.assertEqual(response.data['notes'], 'Test version')
        self.assertFalse(response.data['is_published'])
        
        # Verify version was created in database
        self.assertTrue(FormVersion.objects.filter(form=form, version_number=1).exists())
    
    def test_create_version_and_publish(self):
        """Test creating and immediately publishing a version"""
        form = DynamicFormFactory(slug='test-form')
        page = PageFactory(form=form)
        question = QuestionFactory(page=page)
        
        url = reverse('form-create-version', kwargs={'slug': 'test-form'})
        data = {
            'notes': 'Published version',
            'created_by': 'admin',
            'is_published': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_published'])
        
        # Verify version is published in database
        version = FormVersion.objects.get(form=form, version_number=1)
        self.assertTrue(version.is_published)
    
    def test_create_version_invalid_data(self):
        """Test creating version with invalid data"""
        form = DynamicFormFactory(slug='test-form')
        
        url = reverse('form-create-version', kwargs={'slug': 'test-form'})
        data = {
            'is_published': 'invalid_boolean'  # Invalid boolean value
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FormVersionViewSetTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.form = DynamicFormFactory(slug='test-form')
    
    def test_retrieve_specific_version(self):
        """Test retrieving specific version by version number"""
        version_data = {'form_id': str(self.form.id), 'name': 'Test', 'pages': []}
        version = FormVersionFactory(
            form=self.form,
            version_number=2,
            serialized_form_data=version_data
        )
        
        url = reverse('form-version-detail', kwargs={'form_slug': 'test-form', 'pk': 2})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, version_data)
    
    def test_retrieve_nonexistent_version(self):
        """Test retrieving non-existent version returns 404"""
        url = reverse('form-version-detail', kwargs={'form_slug': 'test-form', 'pk': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_publish_version(self):
        """Test publishing a specific version"""
        version = FormVersionFactory(
            form=self.form,
            version_number=1,
            is_published=False
        )
        
        url = reverse('form-version-publish', kwargs={'form_slug': 'test-form', 'pk': 1})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_published'])
        
        # Verify in database
        version.refresh_from_db()
        self.assertTrue(version.is_published)
    
    def test_publish_nonexistent_version(self):
        """Test publishing non-existent version returns 404"""
        url = reverse('form-version-publish', kwargs={'form_slug': 'test-form', 'pk': 999})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FormSubmissionViewSetTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.form = DynamicFormFactory(slug='test-form')
        self.published_version = PublishedFormVersionFactory(
            form=self.form,
            version_number=1
        )
    
    def test_create_submission_success(self):
        """Test creating a new submission successfully"""
        data = {
            'form_slug': 'test-form',
            'user_session_id': 'session123',
            'user_email': 'test@example.com'
        }
        
        url = reverse('submission-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['form_version_number'], 1)
        self.assertEqual(response.data['user_email'], 'test@example.com')
        
        # Verify submission was created in database
        submission = FormSubmission.objects.get(id=response.data['id'])
        self.assertEqual(submission.form_version, self.published_version)
        self.assertEqual(submission.user_email, 'test@example.com')
    
    def test_create_submission_no_published_version(self):
        """Test creating submission when no published version exists"""
        form = DynamicFormFactory(slug='no-published-form')
        FormVersionFactory(form=form, is_published=False)
        
        data = {'form_slug': 'no-published-form'}
        
        url = reverse('submission-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_create_submission_inactive_form(self):
        """Test creating submission for inactive form"""
        form = DynamicFormFactory(slug='inactive-form', is_active=False)
        
        data = {'form_slug': 'inactive-form'}
        
        url = reverse('submission-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_submission_ip_capture(self):
        """Test that IP address is properly captured"""
        data = {'form_slug': 'test-form'}
        
        url = reverse('submission-list')
        
        # Set HTTP headers to simulate forwarded IP
        response = self.client.post(
            url, 
            data, 
            format='json',
            HTTP_X_FORWARDED_FOR='192.168.1.100,10.0.0.1',
            REMOTE_ADDR='127.0.0.1'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify IP address was captured in database
        submission = FormSubmission.objects.get(id=response.data['id'])
        # The view should capture the first IP from X_FORWARDED_FOR
        self.assertIsNotNone(submission.ip_address)
    
    def test_update_submission_answers(self):
        """Test updating submission answers"""
        submission = FormSubmissionFactory(
            form_version=self.published_version,
            answers={'q1': 'old_answer'},
            is_complete=False
        )
        
        data = {
            'answers': {'q1': 'updated_answer', 'q2': 'new_answer'},
            'is_complete': True
        }
        
        url = reverse('submission-detail', kwargs={'pk': submission.id})
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_complete'])
        
        # Verify in database
        submission.refresh_from_db()
        self.assertEqual(submission.answers['q1'], 'updated_answer')
        self.assertEqual(submission.answers['q2'], 'new_answer')
        self.assertTrue(submission.is_complete)
        self.assertIsNotNone(submission.completed_datetime)
    
    def test_update_submission_merge_answers(self):
        """Test that answers are merged, not replaced"""
        submission = FormSubmissionFactory(
            form_version=self.published_version,
            answers={'q1': 'answer1', 'q2': 'answer2'}
        )
        
        data = {
            'answers': {'q2': 'updated_answer2', 'q3': 'new_answer3'},
            'is_complete': False
        }
        
        url = reverse('submission-detail', kwargs={'pk': submission.id})
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify answers were merged
        submission.refresh_from_db()
        expected_answers = {
            'q1': 'answer1',        # Original answer preserved
            'q2': 'updated_answer2', # Updated answer
            'q3': 'new_answer3'     # New answer added
        }
        self.assertEqual(submission.answers, expected_answers)
    
    def test_update_submission_completion_datetime(self):
        """Test that completion datetime is set when marking complete"""
        submission = FormSubmissionFactory(
            form_version=self.published_version,
            is_complete=False,
            completed_datetime=None
        )
        
        data = {
            'answers': {'q1': 'answer'},
            'is_complete': True
        }
        
        url = reverse('submission-detail', kwargs={'pk': submission.id})
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        submission.refresh_from_db()
        self.assertTrue(submission.is_complete)
        self.assertIsNotNone(submission.completed_datetime)
    
    def test_update_submission_partial(self):
        """Test partial update of submission"""
        submission = FormSubmissionFactory(form_version=self.published_version)
        
        data = {
            'is_complete': True
            # answers field is optional for partial updates
        }
        
        url = reverse('submission-detail', kwargs={'pk': submission.id})
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission.refresh_from_db()
        self.assertTrue(submission.is_complete)
    
    def test_complete_submission_action(self):
        """Test the complete action endpoint"""
        submission = FormSubmissionFactory(
            form_version=self.published_version,
            is_complete=False,
            completed_datetime=None
        )
        
        url = reverse('submission-complete', kwargs={'pk': submission.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_complete'])
        
        # Verify in database
        submission.refresh_from_db()
        self.assertTrue(submission.is_complete)
        self.assertIsNotNone(submission.completed_datetime)
    
    def test_complete_already_completed_submission(self):
        """Test completing an already completed submission"""
        from django.utils import timezone
        original_completion_time = timezone.now()
        
        submission = FormSubmissionFactory(
            form_version=self.published_version,
            is_complete=True,
            completed_datetime=original_completion_time
        )
        
        url = reverse('submission-complete', kwargs={'pk': submission.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify completion datetime wasn't changed
        submission.refresh_from_db()
        self.assertEqual(submission.completed_datetime, original_completion_time)


class APIIntegrationTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
    
    def test_complete_form_workflow(self):
        """Test complete form creation, versioning, and submission workflow"""
        # Create form with structure
        question_type = QuestionTypeFactory(name="Text", slug="text")
        form = DynamicFormFactory(slug='survey-form', name='Survey Form')
        
        page1 = PageFactory(form=form, name='Personal Info', order=1)
        page2 = PageFactory(form=form, name='Preferences', order=2)
        
        name_q = QuestionFactory(page=page1, type=question_type, name='Full Name', order=1)
        email_q = QuestionFactory(page=page1, type=question_type, name='Email', order=2)
        prefs_q = QuestionFactory(page=page2, type=question_type, name='Preferences', order=1)
        
        # Create and publish version
        create_version_url = reverse('form-create-version', kwargs={'slug': 'survey-form'})
        version_data = {
            'notes': 'Initial version',
            'created_by': 'admin',
            'is_published': True
        }
        
        version_response = self.client.post(create_version_url, version_data, format='json')
        self.assertEqual(version_response.status_code, status.HTTP_201_CREATED)
        
        # Retrieve published form
        form_url = reverse('form-detail', kwargs={'slug': 'survey-form'})
        form_response = self.client.get(form_url)
        self.assertEqual(form_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(form_response.data['pages']), 2)
        
        # Create submission
        submission_data = {
            'form_slug': 'survey-form',
            'user_email': 'test@example.com'
        }
        
        submission_url = reverse('submission-list')
        submission_response = self.client.post(submission_url, submission_data, format='json')
        self.assertEqual(submission_response.status_code, status.HTTP_201_CREATED)
        
        submission_id = submission_response.data['id']
        
        # Update submission with answers
        answers_data = {
            'answers': {
                str(name_q.id): 'John Doe',
                str(email_q.id): 'john@example.com',
                str(prefs_q.id): 'Option A'
            },
            'is_complete': False
        }
        
        update_url = reverse('submission-detail', kwargs={'pk': submission_id})
        update_response = self.client.put(update_url, answers_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # Complete submission
        complete_url = reverse('submission-complete', kwargs={'pk': submission_id})
        complete_response = self.client.post(complete_url)
        self.assertEqual(complete_response.status_code, status.HTTP_200_OK)
        self.assertTrue(complete_response.data['is_complete'])
        
        # Verify final state in database
        submission = FormSubmission.objects.get(id=submission_id)
        self.assertTrue(submission.is_complete)
        self.assertIsNotNone(submission.completed_datetime)
        self.assertEqual(len(submission.answers), 3)
    
    def test_error_handling_throughout_workflow(self):
        """Test error handling at each stage of the workflow"""
        # Try to get non-existent form
        url = reverse('form-detail', kwargs={'slug': 'non-existent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Try to create submission for non-existent form
        submission_data = {'form_slug': 'non-existent'}
        url = reverse('submission-list')
        response = self.client.post(url, submission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Try to update non-existent submission
        url = reverse('submission-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = self.client.put(url, {'answers': {}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
