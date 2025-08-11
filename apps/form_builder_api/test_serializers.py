from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import serializers

from apps.form_builder.factories import (
    DynamicFormFactory, FormVersionFactory, PageFactory, QuestionFactory,
    QuestionTypeFactory, FormSubmissionFactory, PublishedFormVersionFactory
)
from .serializers import (
    QuestionTypeSerializer, QuestionSerializer, PageSerializer,
    DynamicFormSerializer, FormVersionSerializer, CreateVersionSerializer,
    FormSubmissionSerializer, CreateSubmissionSerializer, UpdateSubmissionSerializer
)


class QuestionTypeSerializerTests(TestCase):
    
    def test_serialization(self):
        """Test QuestionType serialization"""
        question_type = QuestionTypeFactory(
            name="Text Input",
            slug="text-input",
            description="A basic text input field",
            config={
                'input_type': 'text',
                'validation': {'max_length': 255}
            }
        )
        
        serializer = QuestionTypeSerializer(question_type)
        data = serializer.data
        
        self.assertEqual(data['id'], str(question_type.id))
        self.assertEqual(data['name'], "Text Input")
        self.assertEqual(data['slug'], "text-input")
        self.assertEqual(data['description'], "A basic text input field")
        self.assertEqual(data['config']['input_type'], 'text')
    
    def test_deserialization(self):
        """Test QuestionType deserialization"""
        data = {
            'name': 'Multiple Choice',
            'slug': 'multiple-choice',
            'description': 'A multiple choice question',
            'config': {'options': ['A', 'B', 'C']}
        }
        
        serializer = QuestionTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        question_type = serializer.save()
        
        self.assertEqual(question_type.name, 'Multiple Choice')
        self.assertEqual(question_type.config['options'], ['A', 'B', 'C'])


class QuestionSerializerTests(TestCase):
    
    def test_serialization_with_nested_type(self):
        """Test Question serialization with nested QuestionType"""
        question_type = QuestionTypeFactory(name="Text Input", slug="text")
        question = QuestionFactory(
            type=question_type,
            name="First Name",
            slug="first-name",
            text="What is your first name?",
            required=True,
            config={'placeholder': 'Enter your first name'},
            validation={'min_length': 1, 'max_length': 50}
        )
        
        serializer = QuestionSerializer(question)
        data = serializer.data
        
        self.assertEqual(data['id'], str(question.id))
        self.assertEqual(data['name'], "First Name")
        self.assertEqual(data['type']['name'], "Text Input")
        self.assertEqual(data['type']['slug'], "text")
        self.assertTrue(data['required'])
        self.assertEqual(data['config']['placeholder'], 'Enter your first name')
        self.assertEqual(data['validation']['min_length'], 1)
    
    def test_json_fields_serialization(self):
        """Test that JSON fields are properly serialized"""
        config = {
            'options': [
                {'value': 'yes', 'label': 'Yes'},
                {'value': 'no', 'label': 'No'}
            ],
            'multiple': False
        }
        validation = {
            'required': True,
            'custom_message': 'This field is required'
        }
        conditional_logic = {
            'show_if': {
                'question_slug': 'previous_question',
                'operator': 'equals',
                'value': 'yes'
            }
        }
        
        question = QuestionFactory(
            config=config,
            validation=validation,
            conditional_logic=conditional_logic
        )
        
        serializer = QuestionSerializer(question)
        data = serializer.data
        
        self.assertEqual(data['config'], config)
        self.assertEqual(data['validation'], validation)
        self.assertEqual(data['conditional_logic'], conditional_logic)


class PageSerializerTests(TestCase):
    
    def test_serialization_with_questions(self):
        """Test Page serialization with nested questions"""
        page = PageFactory(name="Personal Info", order=1)
        question1 = QuestionFactory(page=page, name="First Name", order=1)
        question2 = QuestionFactory(page=page, name="Last Name", order=2)
        
        serializer = PageSerializer(page)
        data = serializer.data
        
        self.assertEqual(data['id'], str(page.id))
        self.assertEqual(data['name'], "Personal Info")
        self.assertEqual(data['order'], 1)
        self.assertEqual(len(data['questions']), 2)
        
        # Check questions are properly nested
        question_names = [q['name'] for q in data['questions']]
        self.assertIn("First Name", question_names)
        self.assertIn("Last Name", question_names)
    
    def test_json_fields_serialization(self):
        """Test Page JSON fields serialization"""
        conditional_logic = {
            'show_if': {
                'question_slug': 'show_page',
                'value': 'yes'
            }
        }
        config = {
            'layout': 'two_column',
            'show_progress': True
        }
        
        page = PageFactory(
            conditional_logic=conditional_logic,
            config=config
        )
        
        serializer = PageSerializer(page)
        data = serializer.data
        
        self.assertEqual(data['conditional_logic'], conditional_logic)
        self.assertEqual(data['config'], config)


class DynamicFormSerializerTests(TestCase):
    
    def test_serialization_with_pages(self):
        """Test DynamicForm serialization with nested pages"""
        form = DynamicFormFactory(name="Survey Form", is_active=True)
        page1 = PageFactory(form=form, name="Page 1", order=1)
        page2 = PageFactory(form=form, name="Page 2", order=2)
        
        # Add questions to pages
        QuestionFactory(page=page1, name="Question 1", order=1)
        QuestionFactory(page=page2, name="Question 2", order=1)
        
        serializer = DynamicFormSerializer(form)
        data = serializer.data
        
        self.assertEqual(data['id'], str(form.id))
        self.assertEqual(data['name'], "Survey Form")
        self.assertTrue(data['is_active'])
        self.assertEqual(len(data['pages']), 2)
        
        # Check pages have questions
        self.assertEqual(len(data['pages'][0]['questions']), 1)
        self.assertEqual(len(data['pages'][1]['questions']), 1)


class FormVersionSerializerTests(TestCase):
    
    def test_serialization_with_form_info(self):
        """Test FormVersion serialization with form info"""
        form = DynamicFormFactory(name="Test Form", slug="test-form")
        version = FormVersionFactory(
            form=form,
            version_number=2,
            is_published=True,
            notes="Second version",
            created_by="admin"
        )
        
        serializer = FormVersionSerializer(version)
        data = serializer.data
        
        self.assertEqual(data['id'], str(version.id))
        self.assertEqual(data['form_name'], "Test Form")
        self.assertEqual(data['form_slug'], "test-form")
        self.assertEqual(data['version_number'], 2)
        self.assertTrue(data['is_published'])
        self.assertEqual(data['notes'], "Second version")
        self.assertEqual(data['created_by'], "admin")
    
    def test_serialized_form_data_inclusion(self):
        """Test that serialized_form_data is included"""
        form_data = {
            'form_id': 'test-id',
            'name': 'Test Form',
            'pages': []
        }
        version = FormVersionFactory(serialized_form_data=form_data)
        
        serializer = FormVersionSerializer(version)
        data = serializer.data
        
        self.assertEqual(data['serialized_form_data'], form_data)


class CreateVersionSerializerTests(TestCase):
    
    def test_valid_data(self):
        """Test CreateVersionSerializer with valid data"""
        data = {
            'notes': 'New version with improvements',
            'created_by': 'admin',
            'is_published': True
        }
        
        serializer = CreateVersionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['notes'], 'New version with improvements')
        self.assertEqual(validated_data['created_by'], 'admin')
        self.assertTrue(validated_data['is_published'])
    
    def test_optional_fields(self):
        """Test that all fields are optional"""
        data = {}
        
        serializer = CreateVersionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data.get('notes', ''), '')
        self.assertEqual(validated_data.get('created_by', ''), '')
        self.assertFalse(validated_data.get('is_published', False))
    
    def test_empty_strings_allowed(self):
        """Test that empty strings are allowed"""
        data = {
            'notes': '',
            'created_by': ''
        }
        
        serializer = CreateVersionSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class FormSubmissionSerializerTests(TestCase):
    
    def test_serialization_with_form_info(self):
        """Test FormSubmission serialization with form info"""
        form = DynamicFormFactory(name="Survey Form")
        version = FormVersionFactory(form=form, version_number=3)
        submission = FormSubmissionFactory(
            form_version=version,
            answers={'q1': 'answer1', 'q2': 'answer2'},
            user_email='test@example.com',
            is_complete=True
        )
        
        serializer = FormSubmissionSerializer(submission)
        data = serializer.data
        
        self.assertEqual(data['id'], str(submission.id))
        self.assertEqual(data['form_name'], "Survey Form")
        self.assertEqual(data['form_version_number'], 3)
        self.assertEqual(data['answers'], {'q1': 'answer1', 'q2': 'answer2'})
        self.assertEqual(data['user_email'], 'test@example.com')
        self.assertTrue(data['is_complete'])
    
    def test_complex_answers_serialization(self):
        """Test that complex answer structures are serialized correctly"""
        complex_answers = {
            'text_question': 'Simple text answer',
            'multiple_choice': ['option1', 'option2'],
            'nested_answer': {
                'value': 'other',
                'text': 'Custom answer text'
            },
            'number_answer': 42,
            'boolean_answer': True
        }
        
        submission = FormSubmissionFactory(answers=complex_answers)
        serializer = FormSubmissionSerializer(submission)
        data = serializer.data
        
        self.assertEqual(data['answers'], complex_answers)


class CreateSubmissionSerializerTests(TestCase):
    
    def test_valid_data(self):
        """Test CreateSubmissionSerializer with valid data"""
        data = {
            'form_slug': 'test-form',
            'user_session_id': 'session123',
            'user_email': 'test@example.com'
        }
        
        serializer = CreateSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['form_slug'], 'test-form')
        self.assertEqual(validated_data['user_session_id'], 'session123')
        self.assertEqual(validated_data['user_email'], 'test@example.com')
    
    def test_required_form_slug(self):
        """Test that form_slug is required"""
        data = {
            'user_session_id': 'session123',
            'user_email': 'test@example.com'
        }
        
        serializer = CreateSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('form_slug', serializer.errors)
    
    def test_optional_fields(self):
        """Test that other fields are optional"""
        data = {'form_slug': 'test-form'}
        
        serializer = CreateSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_email_validation(self):
        """Test email field validation"""
        data = {
            'form_slug': 'test-form',
            'user_email': 'invalid-email'
        }
        
        serializer = CreateSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_email', serializer.errors)
        
        # Valid email should work
        data['user_email'] = 'valid@example.com'
        serializer = CreateSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class UpdateSubmissionSerializerTests(TestCase):
    
    def test_valid_data(self):
        """Test UpdateSubmissionSerializer with valid data"""
        answers = {
            'question1': 'Answer 1',
            'question2': ['option1', 'option2'],
            'question3': {'value': 'other', 'text': 'Custom'}
        }
        
        data = {
            'answers': answers,
            'is_complete': True
        }
        
        serializer = UpdateSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['answers'], answers)
        self.assertTrue(validated_data['is_complete'])
    
    def test_required_answers(self):
        """Test that answers field is required"""
        data = {'is_complete': True}
        
        serializer = UpdateSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('answers', serializer.errors)
    
    def test_optional_is_complete(self):
        """Test that is_complete field is optional with default"""
        data = {'answers': {'q1': 'answer'}}
        
        serializer = UpdateSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertFalse(validated_data['is_complete'])
    
    def test_complex_answers_validation(self):
        """Test that complex answer structures are accepted"""
        complex_answers = {
            'text': 'Simple text',
            'array': ['item1', 'item2'],
            'object': {'key': 'value', 'nested': {'deep': 'value'}},
            'number': 123,
            'boolean': True,
            'null_value': None
        }
        
        data = {'answers': complex_answers}
        
        serializer = UpdateSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['answers'], complex_answers)


class SerializerIntegrationTests(TestCase):
    
    def test_form_serialization_hierarchy(self):
        """Test complete form hierarchy serialization"""
        # Create form with full structure
        question_type = QuestionTypeFactory(name="Text", slug="text")
        form = DynamicFormFactory(name="Complete Form")
        page = PageFactory(form=form, name="Page 1", order=1)
        question = QuestionFactory(
            page=page,
            type=question_type,
            name="Question 1",
            order=1,
            config={'placeholder': 'Enter text'},
            validation={'required': True}
        )
        
        # Serialize the complete form
        serializer = DynamicFormSerializer(form)
        data = serializer.data
        
        # Verify complete hierarchy is present
        self.assertEqual(data['name'], "Complete Form")
        self.assertEqual(len(data['pages']), 1)
        
        page_data = data['pages'][0]
        self.assertEqual(page_data['name'], "Page 1")
        self.assertEqual(len(page_data['questions']), 1)
        
        question_data = page_data['questions'][0]
        self.assertEqual(question_data['name'], "Question 1")
        self.assertEqual(question_data['type']['name'], "Text")
        self.assertEqual(question_data['config']['placeholder'], 'Enter text')
        self.assertTrue(question_data['validation']['required'])