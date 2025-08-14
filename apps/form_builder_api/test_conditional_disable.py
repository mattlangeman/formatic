from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.form_builder.models import (
    DynamicForm, FormVersion, Page, Question, QuestionType, FormSubmission
)
import uuid


class ConditionalDisableTestCase(APITestCase):
    """Test cases for conditional disabling of pages and questions."""
    
    def setUp(self):
        """Set up test data."""
        # Create question types
        self.hidden_type = QuestionType.objects.create(
            name="Hidden",
            slug="hidden",
            config={"ui_hidden": True}
        )
        
        self.text_type = QuestionType.objects.create(
            name="Text",
            slug="text"
        )
        
        self.select_type = QuestionType.objects.create(
            name="Select",
            slug="select"
        )
        
        # Create a form
        self.form = DynamicForm.objects.create(
            name="Analysis Tool",
            slug="analysis-tool"
        )
        
        # Create pages
        self.page1 = Page.objects.create(
            form=self.form,
            name="Mode Selection",
            slug="mode-selection",
            order=1
        )
        
        self.page2 = Page.objects.create(
            form=self.form,
            name="Basic Analysis",
            slug="basic-analysis",
            order=2
        )
        
        self.page3 = Page.objects.create(
            form=self.form,
            name="Advanced Analysis",
            slug="advanced-analysis",
            order=3,
            disabled_condition={
                "field": "tool_mode",
                "operator": "equals",
                "value": "free"
            }
        )
        
        # Create questions
        self.tool_mode_question = Question.objects.create(
            page=self.page1,
            type=self.hidden_type,
            name="Tool Mode",
            slug="tool_mode",
            text="Tool Mode",
            order=1,
            config={
                "default_value": "free"
            }
        )
        
        self.basic_input = Question.objects.create(
            page=self.page2,
            type=self.text_type,
            name="Basic Input",
            slug="basic_input",
            text="Enter basic data",
            order=1
        )
        
        self.advanced_input = Question.objects.create(
            page=self.page3,
            type=self.text_type,
            name="Advanced Input",
            slug="advanced_input",
            text="Enter advanced data",
            order=1
        )
        
        self.premium_feature = Question.objects.create(
            page=self.page2,
            type=self.select_type,
            name="Premium Feature",
            slug="premium_feature",
            text="Select premium option",
            order=2,
            disabled_condition={
                "field": "tool_mode",
                "operator": "equals",
                "value": "free"
            },
            config={
                "options": [
                    {"value": "option1", "label": "Option 1"},
                    {"value": "option2", "label": "Option 2"}
                ]
            }
        )
        
        # Create and publish a version
        self.version = self.form.create_version(notes="Initial version")
        self.version.is_published = True
        self.version.save()
    
    def test_page_disabled_condition_in_serialization(self):
        """Test that disabled_condition is included in page serialization."""
        # Use draft endpoint to get current form structure with serializers
        url = reverse('form-draft', args=[self.form.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that page 3 has disabled_condition
        pages = response.data['pages']
        page3_data = next(p for p in pages if p['slug'] == 'advanced-analysis')
        
        self.assertIn('disabled_condition', page3_data)
        self.assertEqual(page3_data['disabled_condition']['field'], 'tool_mode')
        self.assertEqual(page3_data['disabled_condition']['value'], 'free')
        
        # Check is_disabled field exists (defaults to False for backend)
        self.assertIn('is_disabled', page3_data)
        self.assertEqual(page3_data['is_disabled'], False)
    
    def test_question_disabled_condition_in_serialization(self):
        """Test that disabled_condition is included in question serialization."""
        # Use draft endpoint to get current form structure with serializers
        url = reverse('form-draft', args=[self.form.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find the premium feature question
        pages = response.data['pages']
        page2_data = next(p for p in pages if p['slug'] == 'basic-analysis')
        premium_question = next(q for q in page2_data['questions'] if q['slug'] == 'premium_feature')
        
        self.assertIn('disabled_condition', premium_question)
        self.assertEqual(premium_question['disabled_condition']['field'], 'tool_mode')
        self.assertEqual(premium_question['disabled_condition']['value'], 'free')
        
        # Check is_disabled field exists (defaults to False for backend)
        self.assertIn('is_disabled', premium_question)
        self.assertEqual(premium_question['is_disabled'], False)
    
    def test_create_submission_with_initial_answers(self):
        """Test creating a submission with initial answers."""
        url = reverse('submission-list')
        
        # Create submission with premium mode
        data = {
            'form_slug': 'analysis-tool',
            'initial_answers': {
                'tool_mode': 'premium'
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that initial answers were saved
        submission_id = response.data['id']
        submission = FormSubmission.objects.get(id=submission_id)
        
        self.assertEqual(submission.answers.get('tool_mode'), 'premium')
    
    def test_create_submission_with_free_mode(self):
        """Test creating a submission with free mode initial answer."""
        url = reverse('submission-list')
        
        # Create submission with free mode
        data = {
            'form_slug': 'analysis-tool',
            'initial_answers': {
                'tool_mode': 'free'
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that initial answers were saved
        submission_id = response.data['id']
        submission = FormSubmission.objects.get(id=submission_id)
        
        self.assertEqual(submission.answers.get('tool_mode'), 'free')
    
    def test_form_version_includes_disabled_conditions(self):
        """Test that form versions properly serialize disabled conditions."""
        version_data = self.version.serialized_form_data
        
        # Check page disabled condition
        page3_data = next(p for p in version_data['pages'] if p['slug'] == 'advanced-analysis')
        self.assertIn('disabled_condition', page3_data)
        self.assertEqual(page3_data['disabled_condition']['field'], 'tool_mode')
        
        # Check question disabled condition
        page2_data = next(p for p in version_data['pages'] if p['slug'] == 'basic-analysis')
        premium_question = next(q for q in page2_data['questions'] if q['slug'] == 'premium_feature')
        self.assertIn('disabled_condition', premium_question)
        self.assertEqual(premium_question['disabled_condition']['field'], 'tool_mode')
    
    def test_update_page_disabled_condition(self):
        """Test updating a page's disabled condition."""
        url = reverse('builder-page-detail', args=[self.form.slug, self.page2.id])
        
        data = {
            'name': self.page2.name,
            'slug': self.page2.slug,
            'disabled_condition': {
                'field': 'user_type',
                'operator': 'not_equals',
                'value': 'admin'
            }
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the update
        self.page2.refresh_from_db()
        self.assertEqual(self.page2.disabled_condition['field'], 'user_type')
        self.assertEqual(self.page2.disabled_condition['value'], 'admin')
    
    def test_update_question_disabled_condition(self):
        """Test updating a question's disabled condition."""
        url = reverse('builder-question-detail', 
                     args=[self.form.slug, self.page2.id, self.basic_input.id])
        
        data = {
            'name': self.basic_input.name,
            'slug': self.basic_input.slug,
            'text': self.basic_input.text,
            'disabled_condition': {
                'field': 'tool_mode',
                'operator': 'equals',
                'value': 'free'
            }
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the update
        self.basic_input.refresh_from_db()
        self.assertEqual(self.basic_input.disabled_condition['field'], 'tool_mode')
        self.assertEqual(self.basic_input.disabled_condition['value'], 'free')


class DisabledConditionModelTestCase(TestCase):
    """Test model-level disabled condition functionality."""
    
    def test_page_disabled_condition_default(self):
        """Test that disabled_condition defaults to empty dict."""
        form = DynamicForm.objects.create(name="Test Form", slug="test-form")
        page = Page.objects.create(
            form=form,
            name="Test Page",
            slug="test-page",
            order=1
        )
        
        self.assertEqual(page.disabled_condition, {})
    
    def test_question_disabled_condition_default(self):
        """Test that question disabled_condition defaults to empty dict."""
        form = DynamicForm.objects.create(name="Test Form", slug="test-form")
        page = Page.objects.create(form=form, name="Test Page", slug="test-page", order=1)
        question_type = QuestionType.objects.create(name="Text", slug="text")
        
        question = Question.objects.create(
            page=page,
            type=question_type,
            name="Test Question",
            slug="test-question",
            text="Test",
            order=1
        )
        
        self.assertEqual(question.disabled_condition, {})
    
    def test_complex_disabled_condition(self):
        """Test storing complex disabled conditions."""
        form = DynamicForm.objects.create(name="Test Form", slug="test-form")
        page = Page.objects.create(
            form=form,
            name="Test Page",
            slug="test-page",
            order=1,
            disabled_condition={
                "type": "and",
                "conditions": [
                    {"field": "tool_mode", "operator": "equals", "value": "free"},
                    {"field": "user_level", "operator": "less_than", "value": 5}
                ]
            }
        )
        
        self.assertEqual(page.disabled_condition['type'], 'and')
        self.assertEqual(len(page.disabled_condition['conditions']), 2)