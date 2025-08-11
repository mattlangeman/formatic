from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import patch
import json

from .models import (
    DynamicForm, FormVersion, Page, Question, QuestionType, FormSubmission
)
from .factories import (
    DynamicFormFactory, FormVersionFactory, PageFactory, QuestionFactory,
    QuestionTypeFactory, FormSubmissionFactory, PublishedFormVersionFactory,
    CompleteFormSubmissionFactory, TextQuestionFactory, MultiChoiceQuestionFactory
)


class DynamicFormModelTests(TestCase):
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from name"""
        form = DynamicFormFactory(name="My Test Form", slug="")
        form.save()
        self.assertEqual(form.slug, "my-test-form")
    
    def test_slug_preservation_if_provided(self):
        """Test that provided slug is preserved"""
        form = DynamicFormFactory(name="My Test Form", slug="custom-slug")
        form.save()
        self.assertEqual(form.slug, "custom-slug")
    
    def test_get_latest_published_version(self):
        """Test getting the latest published version"""
        form = DynamicFormFactory()
        
        # Create unpublished version
        unpublished = FormVersionFactory(form=form, version_number=1, is_published=False)
        
        # Create published version
        published = FormVersionFactory(form=form, version_number=2, is_published=True)
        
        # Create newer unpublished version
        newer_unpublished = FormVersionFactory(form=form, version_number=3, is_published=False)
        
        latest_published = form.get_latest_published_version()
        self.assertEqual(latest_published, published)
    
    def test_get_latest_published_version_none(self):
        """Test getting latest published version when none exists"""
        form = DynamicFormFactory()
        FormVersionFactory(form=form, is_published=False)
        
        latest_published = form.get_latest_published_version()
        self.assertIsNone(latest_published)
    
    def test_get_current_version_number(self):
        """Test getting next version number"""
        form = DynamicFormFactory()
        
        # No versions yet
        self.assertEqual(form.get_current_version_number(), 1)
        
        # Add version 1
        FormVersionFactory(form=form, version_number=1)
        self.assertEqual(form.get_current_version_number(), 2)
        
        # Add version 2
        FormVersionFactory(form=form, version_number=2)
        self.assertEqual(form.get_current_version_number(), 3)
    
    def test_create_version_basic(self):
        """Test basic version creation"""
        form = DynamicFormFactory()
        page = PageFactory(form=form, order=1)
        question = TextQuestionFactory(page=page, order=1)
        
        version = form.create_version(notes="Test version", created_by="admin")
        
        self.assertEqual(version.form, form)
        self.assertEqual(version.version_number, 1)
        self.assertEqual(version.notes, "Test version")
        self.assertEqual(version.created_by, "admin")
        self.assertFalse(version.is_published)
        
        # Check serialized data structure
        data = version.serialized_form_data
        self.assertEqual(data['form_id'], str(form.id))
        self.assertEqual(data['name'], form.name)
        self.assertEqual(data['slug'], form.slug)
        self.assertEqual(len(data['pages']), 1)
        self.assertEqual(len(data['pages'][0]['questions']), 1)
    
    def test_create_version_with_multiple_pages_and_questions(self):
        """Test version creation with complex form structure"""
        form = DynamicFormFactory()
        
        # Create pages with questions
        page1 = PageFactory(form=form, order=1)
        page2 = PageFactory(form=form, order=2)
        
        q1 = TextQuestionFactory(page=page1, order=1)
        q2 = TextQuestionFactory(page=page1, order=2)
        q3 = MultiChoiceQuestionFactory(page=page2, order=1)
        
        version = form.create_version()
        data = version.serialized_form_data
        
        self.assertEqual(len(data['pages']), 2)
        self.assertEqual(len(data['pages'][0]['questions']), 2)
        self.assertEqual(len(data['pages'][1]['questions']), 1)
        
        # Check ordering is preserved
        self.assertEqual(data['pages'][0]['order'], 1)
        self.assertEqual(data['pages'][1]['order'], 2)
        self.assertEqual(data['pages'][0]['questions'][0]['order'], 1)
        self.assertEqual(data['pages'][0]['questions'][1]['order'], 2)
    
    def test_string_representation(self):
        """Test model string representation"""
        form = DynamicFormFactory(name="Test Form")
        self.assertEqual(str(form), "Test Form")


class FormVersionModelTests(TestCase):
    
    def test_unique_version_number_per_form(self):
        """Test that version numbers must be unique per form"""
        form = DynamicFormFactory()
        FormVersionFactory(form=form, version_number=1)
        
        with self.assertRaises(IntegrityError):
            FormVersionFactory(form=form, version_number=1)
    
    def test_same_version_number_different_forms(self):
        """Test that same version numbers can exist for different forms"""
        form1 = DynamicFormFactory()
        form2 = DynamicFormFactory()
        
        v1 = FormVersionFactory(form=form1, version_number=1)
        v2 = FormVersionFactory(form=form2, version_number=1)
        
        self.assertNotEqual(v1.form, v2.form)
        self.assertEqual(v1.version_number, v2.version_number)
    
    def test_string_representation(self):
        """Test version string representation"""
        form = DynamicFormFactory(name="Test Form")
        version = FormVersionFactory(form=form, version_number=2)
        self.assertEqual(str(version), "Test Form v2")
    
    def test_ordering(self):
        """Test versions are ordered by version number descending"""
        form = DynamicFormFactory()
        v1 = FormVersionFactory(form=form, version_number=1)
        v3 = FormVersionFactory(form=form, version_number=3)
        v2 = FormVersionFactory(form=form, version_number=2)
        
        versions = list(form.versions.all())
        self.assertEqual(versions, [v3, v2, v1])


class PageModelTests(TestCase):
    
    def test_slug_auto_generation(self):
        """Test page slug auto-generation"""
        page = PageFactory(name="Introduction Page", slug="")
        page.save()
        self.assertEqual(page.slug, "introduction-page")
    
    def test_unique_order_per_form(self):
        """Test that page order must be unique within a form"""
        form = DynamicFormFactory()
        PageFactory(form=form, order=1)
        
        with self.assertRaises(IntegrityError):
            PageFactory(form=form, order=1)
    
    def test_unique_slug_per_form(self):
        """Test that page slug must be unique within a form"""
        form = DynamicFormFactory()
        PageFactory(form=form, slug="intro")
        
        with self.assertRaises(IntegrityError):
            PageFactory(form=form, slug="intro")
    
    def test_same_order_different_forms(self):
        """Test that same order can exist in different forms"""
        form1 = DynamicFormFactory()
        form2 = DynamicFormFactory()
        
        page1 = PageFactory(form=form1, order=1)
        page2 = PageFactory(form=form2, order=1)
        
        self.assertNotEqual(page1.form, page2.form)
        self.assertEqual(page1.order, page2.order)
    
    def test_string_representation(self):
        """Test page string representation"""
        form = DynamicFormFactory(name="Test Form")
        page = PageFactory(form=form, name="Page 1")
        self.assertEqual(str(page), "Test Form - Page 1")
    
    def test_json_fields_default_values(self):
        """Test that JSON fields have proper default values"""
        page = PageFactory(conditional_logic={}, config={})
        self.assertIsInstance(page.conditional_logic, dict)
        self.assertIsInstance(page.config, dict)


class QuestionTypeModelTests(TestCase):
    
    def test_slug_auto_generation(self):
        """Test question type slug auto-generation"""
        qtype = QuestionTypeFactory(name="Text Input", slug="")
        qtype.save()
        self.assertEqual(qtype.slug, "text-input")
    
    def test_unique_slug(self):
        """Test that question type slugs must be unique"""
        QuestionTypeFactory(slug="text-input")
        
        with self.assertRaises(IntegrityError):
            QuestionTypeFactory(slug="text-input")
    
    def test_string_representation(self):
        """Test question type string representation"""
        qtype = QuestionTypeFactory(name="Multiple Choice")
        self.assertEqual(str(qtype), "Multiple Choice")
    
    def test_config_json_field(self):
        """Test that config is properly stored as JSON"""
        config_data = {
            'input_type': 'select',
            'multiple': True,
            'options': ['A', 'B', 'C']
        }
        qtype = QuestionTypeFactory(config=config_data)
        self.assertEqual(qtype.config, config_data)


class QuestionModelTests(TestCase):
    
    def test_slug_auto_generation(self):
        """Test question slug auto-generation"""
        question = QuestionFactory(name="First Name", slug="")
        question.save()
        self.assertEqual(question.slug, "first-name")
    
    def test_unique_order_per_page(self):
        """Test that question order must be unique within a page"""
        page = PageFactory()
        QuestionFactory(page=page, order=1)
        
        with self.assertRaises(IntegrityError):
            QuestionFactory(page=page, order=1)
    
    def test_same_order_different_pages(self):
        """Test that same order can exist in different pages"""
        page1 = PageFactory()
        page2 = PageFactory()
        
        q1 = QuestionFactory(page=page1, order=1)
        q2 = QuestionFactory(page=page2, order=1)
        
        self.assertNotEqual(q1.page, q2.page)
        self.assertEqual(q1.order, q2.order)
    
    def test_string_representation(self):
        """Test question string representation"""
        page = PageFactory(name="Page 1")
        question = QuestionFactory(page=page, name="Question 1")
        self.assertEqual(str(question), "Page 1 - Question 1")
    
    def test_json_fields_functionality(self):
        """Test that all JSON fields work correctly"""
        config = {'placeholder': 'Enter text', 'max_length': 100}
        validation = {'required': True, 'min_length': 5}
        logic = {'show_if': {'question': 'q1', 'value': 'yes'}}
        
        question = QuestionFactory(
            config=config,
            validation=validation,
            conditional_logic=logic
        )
        
        self.assertEqual(question.config, config)
        self.assertEqual(question.validation, validation)
        self.assertEqual(question.conditional_logic, logic)


class FormSubmissionModelTests(TestCase):
    
    def test_string_representation(self):
        """Test submission string representation"""
        form = DynamicFormFactory(name="Survey Form")
        version = FormVersionFactory(form=form, version_number=1)
        submission = FormSubmissionFactory(form_version=version, is_complete=True)
        
        expected = f"Survey Form v1 - Complete ({submission.created_datetime.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(submission), expected)
    
    def test_incomplete_submission_representation(self):
        """Test incomplete submission string representation"""
        form = DynamicFormFactory(name="Survey Form")
        version = FormVersionFactory(form=form, version_number=1)
        submission = FormSubmissionFactory(form_version=version, is_complete=False)
        
        expected = f"Survey Form v1 - In Progress ({submission.created_datetime.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(submission), expected)
    
    def test_answers_json_field(self):
        """Test that answers are properly stored as JSON"""
        answers_data = {
            'question_1': 'Answer 1',
            'question_2': ['Option A', 'Option B'],
            'question_3': {'value': 'other', 'text': 'Custom answer'}
        }
        submission = FormSubmissionFactory(answers=answers_data)
        self.assertEqual(submission.answers, answers_data)
    
    def test_completion_datetime_logic(self):
        """Test completion datetime is set appropriately"""
        submission = FormSubmissionFactory(is_complete=False, completed_datetime=None)
        self.assertIsNone(submission.completed_datetime)
        
        complete_submission = CompleteFormSubmissionFactory()
        self.assertIsNotNone(complete_submission.completed_datetime)


class ModelIntegrationTests(TestCase):
    
    def test_full_form_structure_creation(self):
        """Test creating a complete form with all relationships"""
        # Create question types
        text_type = QuestionTypeFactory(name="Text Input", slug="text")
        choice_type = QuestionTypeFactory(name="Multiple Choice", slug="choice")
        
        # Create form
        form = DynamicFormFactory(name="Customer Survey")
        
        # Create pages
        page1 = PageFactory(form=form, name="Personal Info", order=1)
        page2 = PageFactory(form=form, name="Preferences", order=2)
        
        # Create questions
        name_q = QuestionFactory(page=page1, type=text_type, name="Full Name", order=1)
        email_q = QuestionFactory(page=page1, type=text_type, name="Email", order=2)
        prefs_q = QuestionFactory(page=page2, type=choice_type, name="Preferences", order=1)
        
        # Create and test version
        version = form.create_version(notes="Initial version", created_by="admin")
        
        # Verify structure
        self.assertEqual(form.pages.count(), 2)
        self.assertEqual(page1.questions.count(), 2)
        self.assertEqual(page2.questions.count(), 1)
        
        # Verify version data
        data = version.serialized_form_data
        self.assertEqual(len(data['pages']), 2)
        self.assertEqual(len(data['pages'][0]['questions']), 2)
        self.assertEqual(len(data['pages'][1]['questions']), 1)
        
        # Create submission
        version.is_published = True
        version.save()
        
        submission = FormSubmissionFactory(
            form_version=version,
            answers={
                str(name_q.id): "John Doe",
                str(email_q.id): "john@example.com",
                str(prefs_q.id): ["option1", "option2"]
            }
        )
        
        self.assertEqual(submission.form_version, version)
        self.assertIn(str(name_q.id), submission.answers)
    
    def test_cascade_deletion(self):
        """Test that cascade deletions work properly"""
        form = DynamicFormFactory()
        page = PageFactory(form=form)
        question = QuestionFactory(page=page)
        version = FormVersionFactory(form=form)
        submission = FormSubmissionFactory(form_version=version)
        
        # Delete form should cascade to all related objects
        form_id = form.id
        page_id = page.id
        question_id = question.id
        version_id = version.id
        submission_id = submission.id
        
        form.delete()
        
        # Verify all related objects are deleted
        self.assertFalse(DynamicForm.objects.filter(id=form_id).exists())
        self.assertFalse(Page.objects.filter(id=page_id).exists())
        self.assertFalse(Question.objects.filter(id=question_id).exists())
        self.assertFalse(FormVersion.objects.filter(id=version_id).exists())
        self.assertFalse(FormSubmission.objects.filter(id=submission_id).exists())
