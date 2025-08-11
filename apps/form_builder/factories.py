import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyFunction, LazyAttribute
import json
import random
from django.utils.text import slugify
from .models import DynamicForm, FormVersion, Page, Question, QuestionType, FormSubmission


class QuestionTypeFactory(DjangoModelFactory):
    class Meta:
        model = QuestionType
    
    name = Faker('word')
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    description = Faker('sentence')
    config = LazyFunction(lambda: {
        'input_type': random.choice(['text', 'number', 'email']),
        'validation': {
            'required': random.choice([True, False]),
            'min_length': random.randint(1, 10)
        },
        'ui_options': {
            'placeholder': 'Enter value',
            'help_text': 'Help text for this field'
        }
    })


class DynamicFormFactory(DjangoModelFactory):
    class Meta:
        model = DynamicForm
    
    name = Faker('sentence', nb_words=3)
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    is_active = True


class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page
    
    form = SubFactory(DynamicFormFactory)
    name = Faker('sentence', nb_words=2)
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    order = Faker('random_int', min=1, max=10)
    conditional_logic = LazyFunction(lambda: {
        'show_if': {
            'question_slug': 'test_question',
            'operator': random.choice(['equals', 'not_equals', 'contains']),
            'value': 'test_value'
        },
        'required_if': {
            'question_slug': 'required_question',
            'value': 'required_value'
        }
    })
    config = LazyFunction(lambda: {
        'layout': random.choice(['single_column', 'two_column']),
        'progress_bar': random.choice([True, False]),
        'navigation': {
            'show_back': random.choice([True, False]),
            'show_next': random.choice([True, False])
        }
    })


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question
    
    page = SubFactory(PageFactory)
    type = SubFactory(QuestionTypeFactory)
    name = Faker('sentence', nb_words=2)
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    text = Faker('sentence')
    subtext = Faker('sentence')
    required = Faker('boolean')
    order = Faker('random_int', min=1, max=10)
    config = LazyFunction(lambda: {
        'options': [
            {
                'value': f'option_{i}',
                'label': f'Option {i}'
            } for i in range(1, random.randint(3, 5))
        ],
        'multiple': random.choice([True, False]),
        'other_option': random.choice([True, False])
    })
    validation = LazyFunction(lambda: {
        'min_length': random.randint(1, 100),
        'max_length': random.randint(101, 500),
        'pattern': r'[A-Za-z0-9]{5,10}',
        'custom_message': 'This field is required'
    })
    conditional_logic = LazyFunction(lambda: {
        'show_if': {
            'question_slug': 'show_condition',
            'operator': 'equals',
            'value': 'yes'
        },
        'skip_if': {
            'question_slug': 'skip_condition',
            'value': 'no'
        }
    })


class FormVersionFactory(DjangoModelFactory):
    class Meta:
        model = FormVersion
    
    form = SubFactory(DynamicFormFactory)
    version_number = Faker('random_int', min=1, max=10)
    is_published = Faker('boolean')
    notes = Faker('sentence')
    created_by = Faker('name')
    serialized_form_data = LazyFunction(lambda: {
        'form_id': '12345678-1234-5678-9012-123456789012',
        'name': 'Sample Form',
        'slug': 'sample-form',
        'pages': [
            {
                'id': f'page-{i+1}',
                'name': f'Page {i+1}',
                'slug': f'page-{i+1}',
                'order': i + 1,
                'conditional_logic': {},
                'config': {'layout': 'single_column'},
                'questions': [
                    {
                        'id': f'question-{i+1}-{j+1}',
                        'type': 'text',
                        'name': f'Question {j+1}',
                        'slug': f'question-{j+1}',
                        'text': f'What is your answer for question {j+1}?',
                        'subtext': 'Please provide a detailed answer',
                        'required': random.choice([True, False]),
                        'config': {},
                        'validation': {},
                        'conditional_logic': {},
                        'order': j + 1
                    } for j in range(random.randint(1, 3))
                ]
            } for i in range(random.randint(1, 2))
        ]
    })


class FormSubmissionFactory(DjangoModelFactory):
    class Meta:
        model = FormSubmission
    
    form_version = SubFactory(FormVersionFactory)
    user_session_id = Faker('uuid4')
    user_email = Faker('email')
    ip_address = Faker('ipv4')
    is_complete = Faker('boolean')
    answers = LazyFunction(lambda: {
        'question_1': 'Sample text answer',
        'question_2': random.randint(1, 100),
        'question_3': [
            f'choice_{i}' for i in range(1, random.randint(2, 4))
        ],
        'question_4': {
            'value': 'other_value',
            'other': 'Custom other answer'
        }
    })


# Specialized factories for common test scenarios
class PublishedFormVersionFactory(FormVersionFactory):
    is_published = True


class CompleteFormSubmissionFactory(FormSubmissionFactory):
    is_complete = True
    completed_datetime = Faker('date_time_this_year')


class SimpleQuestionTypeFactory(QuestionTypeFactory):
    config = LazyFunction(lambda: {
        'input_type': 'text',
        'validation': {'required': True}
    })


class TextQuestionFactory(QuestionFactory):
    type = SubFactory(SimpleQuestionTypeFactory)
    config = LazyFunction(lambda: {
        'placeholder': 'Enter your answer here',
        'multiline': False
    })
    validation = LazyFunction(lambda: {
        'min_length': 1,
        'max_length': 255
    })


class MultiChoiceQuestionFactory(QuestionFactory):
    config = LazyFunction(lambda: {
        'options': [
            {'value': 'option1', 'label': 'Option 1'},
            {'value': 'option2', 'label': 'Option 2'},
            {'value': 'option3', 'label': 'Option 3'}
        ],
        'multiple': True,
        'other_option': True
    })