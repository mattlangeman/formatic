from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, extend_schema_field, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from apps.form_builder.models import DynamicForm, FormVersion, FormSubmission, Page, Question, QuestionType, QuestionGroup, QuestionGroupTemplate
from .schemas import (
    QUESTION_CONFIG_SCHEMA, VALIDATION_CONFIG_SCHEMA, CONDITIONAL_LOGIC_SCHEMA,
    PAGE_CONFIG_SCHEMA, SERIALIZED_FORM_DATA_SCHEMA, SUBMISSION_ANSWERS_SCHEMA
)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Text Question Type',
            summary='Configuration for text input questions',
            value={
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Text Input",
                "slug": "text",
                "description": "Single line text input field",
                "config": {
                    "default_placeholder": "Enter text here",
                    "supports_validation": True,
                    "max_length_default": 255
                }
            }
        ),
        OpenApiExample(
            'Select Question Type',
            summary='Configuration for select/dropdown questions',
            value={
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "name": "Select Dropdown",
                "slug": "select",
                "description": "Dropdown selection with predefined options",
                "config": {
                    "supports_multiple": False,
                    "requires_options": True,
                    "searchable": True
                }
            }
        )
    ]
)
class QuestionTypeSerializer(serializers.ModelSerializer):
    """Serializer for question types with their configuration options."""
    
    @extend_schema_field(QUESTION_CONFIG_SCHEMA)
    def get_config(self, obj):
        return obj.config
    
    class Meta:
        model = QuestionType
        fields = ['id', 'name', 'slug', 'description', 'config']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Email Question',
            summary='Email input question with validation',
            value={
                "id": "789e0123-e89b-12d3-a456-426614174002",
                "name": "Email Address",
                "slug": "email_address",
                "text": "What is your email address?",
                "subtext": "We'll use this to send you updates",
                "required": True,
                "config": {
                    "placeholder": "your@email.com",
                    "max_length": 255
                },
                "validation": {
                    "required": True,
                    "email": True,
                    "custom_error_message": "Please enter a valid email address"
                },
                "conditional_logic": {},
                "order": 1,
                "type": {
                    "slug": "email",
                    "name": "Email Input"
                }
            }
        )
    ]
)
class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for individual questions with full configuration."""
    type = QuestionTypeSerializer(read_only=True)
    
    @extend_schema_field(QUESTION_CONFIG_SCHEMA)
    def get_config(self, obj):
        return obj.config
        
    @extend_schema_field(VALIDATION_CONFIG_SCHEMA)
    def get_validation(self, obj):
        return obj.validation
        
    @extend_schema_field(CONDITIONAL_LOGIC_SCHEMA)
    def get_conditional_logic(self, obj):
        return obj.conditional_logic

    class Meta:
        model = Question
        fields = [
            'id', 'name', 'slug', 'text', 'subtext', 'required', 
            'config', 'validation', 'conditional_logic', 'order', 'type'
        ]


class FormQuestionSerializer(serializers.ModelSerializer):
    """Lightweight serializer for questions in form contexts - references type by slug only."""
    type = serializers.CharField(source='type.slug', read_only=True)
    is_disabled = serializers.SerializerMethodField()
    
    @extend_schema_field(QUESTION_CONFIG_SCHEMA)
    def get_config(self, obj):
        return obj.config
        
    @extend_schema_field(VALIDATION_CONFIG_SCHEMA)
    def get_validation(self, obj):
        return obj.validation
        
    @extend_schema_field(CONDITIONAL_LOGIC_SCHEMA)
    def get_conditional_logic(self, obj):
        return obj.conditional_logic
    
    @extend_schema_field(CONDITIONAL_LOGIC_SCHEMA)
    def get_disabled_condition(self, obj):
        return obj.disabled_condition
    
    def get_is_disabled(self, obj):
        """Evaluate if question should be disabled based on conditions."""
        # This will be evaluated on the frontend based on current form answers
        # We just pass the condition for the frontend to evaluate
        return False  # Default to not disabled, frontend will evaluate

    class Meta:
        model = Question
        fields = [
            'id', 'name', 'slug', 'text', 'subtext', 'required', 
            'config', 'validation', 'conditional_logic', 'disabled_condition',
            'order', 'type', 'is_disabled'
        ]


class QuestionGroupSerializer(serializers.ModelSerializer):
    """Serializer for question groups with their nested questions."""
    questions = FormQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuestionGroup
        fields = [
            'id', 'name', 'slug', 'display_type', 'config', 'order', 'questions'
        ]


class FormPageSerializer(serializers.ModelSerializer):
    """Lightweight serializer for pages in form contexts - uses minimal question data."""
    questions = serializers.SerializerMethodField()
    question_groups = QuestionGroupSerializer(many=True, read_only=True)
    is_disabled = serializers.SerializerMethodField()
    
    def get_questions(self, obj):
        # Only get questions directly on page (not in groups)
        questions = obj.questions.filter(question_group__isnull=True).order_by('order')
        return FormQuestionSerializer(questions, many=True).data
    
    @extend_schema_field(CONDITIONAL_LOGIC_SCHEMA)
    def get_conditional_logic(self, obj):
        return obj.conditional_logic
    
    @extend_schema_field(CONDITIONAL_LOGIC_SCHEMA)
    def get_disabled_condition(self, obj):
        return obj.disabled_condition
        
    @extend_schema_field(PAGE_CONFIG_SCHEMA)
    def get_config(self, obj):
        return obj.config
    
    def get_is_disabled(self, obj):
        """Evaluate if page should be disabled based on conditions."""
        # This will be evaluated on the frontend based on current form answers
        # We just pass the condition for the frontend to evaluate
        return False  # Default to not disabled, frontend will evaluate

    class Meta:
        model = Page
        fields = [
            'id', 'name', 'slug', 'order', 'conditional_logic', 'disabled_condition',
            'config', 'questions', 'question_groups', 'is_disabled'
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Contact Information Page',
            summary='Form page with contact questions',
            value={
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "name": "Contact Information",
                "slug": "contact-info",
                "order": 1,
                "conditional_logic": {},
                "config": {
                    "show_progress": True,
                    "theme": "modern",
                    "allow_back": True
                },
                "questions": [
                    {
                        "id": "q1",
                        "name": "Full Name",
                        "slug": "full_name",
                        "text": "What is your full name?",
                        "required": True,
                        "type": {"slug": "text", "name": "Text Input"}
                    }
                ]
            }
        )
    ]
)
class PageSerializer(serializers.ModelSerializer):
    """Serializer for form pages with their questions."""
    questions = serializers.SerializerMethodField()
    question_groups = QuestionGroupSerializer(many=True, read_only=True)
    
    def get_questions(self, obj):
        # Only get questions directly on page (not in groups)
        questions = obj.questions.filter(question_group__isnull=True).order_by('order')
        return QuestionSerializer(questions, many=True).data
    
    @extend_schema_field(CONDITIONAL_LOGIC_SCHEMA)
    def get_conditional_logic(self, obj):
        return obj.conditional_logic
        
    @extend_schema_field(PAGE_CONFIG_SCHEMA)
    def get_config(self, obj):
        return obj.config

    class Meta:
        model = Page
        fields = [
            'id', 'name', 'slug', 'order', 'conditional_logic', 
            'config', 'questions', 'question_groups'
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Customer Survey Form',
            summary='Complete form structure with multiple pages',
            value={
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Customer Feedback Survey",
                "slug": "customer-feedback-survey",
                "is_active": True,
                "pages": [
                    {
                        "id": "page-1",
                        "name": "Basic Information",
                        "slug": "basic-info",
                        "order": 1,
                        "questions": [
                            {
                                "id": "q1",
                                "name": "Full Name",
                                "text": "What is your full name?",
                                "required": True,
                                "type": {"slug": "text"}
                            }
                        ]
                    }
                ]
            }
        )
    ]
)
class DynamicFormSerializer(serializers.ModelSerializer):
    """Serializer for dynamic forms with lightweight page and question structure."""
    pages = FormPageSerializer(many=True, read_only=True)

    class Meta:
        model = DynamicForm
        fields = ['id', 'name', 'slug', 'is_active', 'pages']


class FullDynamicFormSerializer(serializers.ModelSerializer):
    """Serializer for dynamic forms with complete page and question structure (including full type data)."""
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = DynamicForm
        fields = ['id', 'name', 'slug', 'is_active', 'pages']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Published Form Version',
            summary='A published version with complete serialized form data',
            value={
                "id": "version-123e4567-e89b-12d3-a456-426614174000",
                "form_name": "Customer Survey",
                "form_slug": "customer-survey",
                "version_number": 2,
                "serialized_form_data": {
                    "form_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Customer Survey",
                    "slug": "customer-survey",
                    "pages": [
                        {
                            "id": "page-1",
                            "name": "Contact Info",
                            "questions": [
                                {
                                    "id": "q1",
                                    "type": "email",
                                    "slug": "email",
                                    "text": "Your email?",
                                    "required": True
                                }
                            ]
                        }
                    ]
                },
                "is_published": True,
                "notes": "Updated email validation",
                "created_datetime": "2024-01-15T10:30:00Z",
                "created_by": "admin@example.com"
            }
        )
    ]
)
class FormVersionSerializer(serializers.ModelSerializer):
    """Serializer for form versions with complete serialized data."""
    form_name = serializers.CharField(source='form.name', read_only=True)
    form_slug = serializers.CharField(source='form.slug', read_only=True)
    
    @extend_schema_field(SERIALIZED_FORM_DATA_SCHEMA)
    def get_serialized_form_data(self, obj):
        return obj.serialized_form_data

    class Meta:
        model = FormVersion
        fields = [
            'id', 'form_name', 'form_slug', 'version_number', 
            'serialized_form_data', 'is_published', 'notes', 
            'created_datetime', 'created_by'
        ]


class CreateVersionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    created_by = serializers.CharField(required=False, allow_blank=True)
    is_published = serializers.BooleanField(default=False)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Completed Submission',
            summary='A completed form submission with all answers',
            value={
                "id": "sub-123e4567-e89b-12d3-a456-426614174000",
                "form_name": "Customer Survey",
                "form_version_number": 2,
                "answers": {
                    "full_name": "John Doe",
                    "email_address": "john@example.com",
                    "age": 30,
                    "interests": ["technology", "sports"],
                    "newsletter_signup": True,
                    "rating": 8,
                    "comments": "Great service!"
                },
                "user_session_id": "sess_abc123",
                "user_email": "john@example.com",
                "ip_address": "192.168.1.100",
                "is_complete": True,
                "started_datetime": "2024-01-15T09:00:00Z",
                "completed_datetime": "2024-01-15T09:15:00Z",
                "created_datetime": "2024-01-15T09:00:00Z"
            }
        ),
        OpenApiExample(
            'In Progress Submission',
            summary='A partially completed submission',
            value={
                "id": "sub-456e7890-e89b-12d3-a456-426614174001",
                "form_name": "Customer Survey",
                "form_version_number": 2,
                "answers": {
                    "full_name": "Jane Smith",
                    "email_address": "jane@example.com"
                },
                "user_session_id": "sess_def456",
                "user_email": "jane@example.com",
                "ip_address": "192.168.1.101",
                "is_complete": False,
                "started_datetime": "2024-01-15T10:00:00Z",
                "completed_datetime": None,
                "created_datetime": "2024-01-15T10:00:00Z"
            }
        )
    ]
)
class FormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for form submissions with user responses."""
    form_name = serializers.CharField(source='form_version.form.name', read_only=True)
    form_version_number = serializers.IntegerField(source='form_version.version_number', read_only=True)
    
    @extend_schema_field(SUBMISSION_ANSWERS_SCHEMA)
    def get_answers(self, obj):
        return obj.answers

    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form_name', 'form_version_number', 'answers',
            'user_session_id', 'user_email', 'ip_address', 'is_complete',
            'started_datetime', 'completed_datetime', 'created_datetime', 'modified_datetime'
        ]


class CreateSubmissionSerializer(serializers.Serializer):
    form_slug = serializers.CharField()
    user_session_id = serializers.CharField(required=False, allow_blank=True)
    user_email = serializers.EmailField(required=False, allow_blank=True)
    initial_answers = serializers.JSONField(required=False, default=dict, help_text="Initial answers to pre-populate the form")


class UpdateSubmissionSerializer(serializers.Serializer):
    answers = serializers.JSONField(required=False)
    is_complete = serializers.BooleanField(default=False, required=False)


# Form Builder Serializers

class CreatePageSerializer(serializers.ModelSerializer):
    """Serializer for creating new pages."""
    
    class Meta:
        model = Page
        fields = ['name', 'slug', 'conditional_logic', 'disabled_condition', 'config']
        

class UpdatePageSerializer(serializers.ModelSerializer):
    """Serializer for updating existing pages."""
    
    class Meta:
        model = Page
        fields = ['name', 'slug', 'conditional_logic', 'disabled_condition', 'config']


class CreateQuestionSerializer(serializers.ModelSerializer):
    """Serializer for creating new questions."""
    type_slug = serializers.CharField(write_only=True)
    
    class Meta:
        model = Question
        fields = [
            'name', 'slug', 'text', 'subtext', 'required', 
            'config', 'validation', 'conditional_logic', 'disabled_condition', 'type_slug'
        ]
    
    def create(self, validated_data):
        # Remove type_slug from validated_data since it's not a model field
        validated_data.pop('type_slug', None)
        return super().create(validated_data)


class UpdateQuestionSerializer(serializers.ModelSerializer):
    """Serializer for updating existing questions."""
    
    class Meta:
        model = Question
        fields = [
            'name', 'slug', 'text', 'subtext', 'required', 
            'config', 'validation', 'conditional_logic', 'disabled_condition'
        ]


class CreateFormSerializer(serializers.ModelSerializer):
    """Serializer for creating new forms."""
    skip_default_page = serializers.BooleanField(default=False, write_only=True)
    
    class Meta:
        model = DynamicForm
        fields = ['name', 'slug', 'skip_default_page']


class CreateQuestionGroupSerializer(serializers.ModelSerializer):
    """Serializer for creating new question groups."""
    
    class Meta:
        model = QuestionGroup
        fields = ['name', 'slug', 'display_type', 'config']


class UpdateQuestionGroupSerializer(serializers.ModelSerializer):
    """Serializer for updating question groups."""
    
    class Meta:
        model = QuestionGroup
        fields = ['name', 'slug', 'display_type', 'config']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Address Template',
            summary='Address group template with street, city, country, state, postal code',
            value={
                "id": "dd3cd14a-7e3b-420a-9e47-874dd6170331",
                "name": "Address",
                "slug": "address",
                "description": "Complete address information including street, city, state/province, and postal code",
                "display_type": "address",
                "config": {
                    "layout": "stacked",
                    "show_labels": True,
                    "validation": {
                        "required_fields": ["street", "city", "country"]
                    }
                },
                "question_template": [
                    {
                        "type_slug": "short-text",
                        "name": "Street Address",
                        "slug_suffix": "street",
                        "text": "Street Address",
                        "required": True,
                        "config": {"placeholder": "123 Main Street"}
                    },
                    {
                        "type_slug": "short-text",
                        "name": "City",
                        "slug_suffix": "city", 
                        "text": "City",
                        "required": True
                    },
                    {
                        "type_slug": "dropdown",
                        "name": "Country",
                        "slug_suffix": "country",
                        "text": "Country",
                        "required": True,
                        "config": {
                            "options": [
                                {"value": "US", "label": "United States"},
                                {"value": "CA", "label": "Canada"}
                            ]
                        }
                    }
                ]
            }
        )
    ]
)
class QuestionGroupTemplateSerializer(serializers.ModelSerializer):
    """Serializer for question group templates."""
    
    class Meta:
        model = QuestionGroupTemplate
        fields = [
            'id', 'name', 'slug', 'description', 'display_type', 
            'config', 'question_template', 'is_active',
            'created_datetime', 'modified_datetime'
        ]
        read_only_fields = ['id', 'created_datetime', 'modified_datetime']