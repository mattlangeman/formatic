"""
OpenAPI schema definitions for JSON fields in the Formatic API.

This module defines the structure of complex JSON fields used throughout
the application, providing type safety and documentation for the API.
"""

# Schema for conditional logic used in pages and questions
CONDITIONAL_LOGIC_SCHEMA = {
    "type": "object",
    "description": "Rules that determine when a page or question should be shown/hidden",
    "properties": {
        "show_if": {
            "type": "object",
            "description": "Show this element only if these conditions are met",
            "additionalProperties": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "boolean"},
                    {"type": "array", "items": {"type": "string"}}
                ]
            },
            "example": {
                "user_type": "premium",
                "age": 18,
                "interests": ["technology", "science"]
            }
        },
        "hide_if": {
            "type": "object",
            "description": "Hide this element if these conditions are met",
            "additionalProperties": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"}, 
                    {"type": "boolean"},
                    {"type": "array", "items": {"type": "string"}}
                ]
            }
        },
        "operator": {
            "type": "string",
            "enum": ["AND", "OR"],
            "default": "AND",
            "description": "Logic operator for multiple conditions"
        }
    },
    "additionalProperties": True,
    "example": {
        "show_if": {
            "previous_question": "yes",
            "user_age": 18
        },
        "operator": "AND"
    }
}

# Schema for page configuration
PAGE_CONFIG_SCHEMA = {
    "type": "object",
    "description": "Configuration options for form pages",
    "properties": {
        "show_progress": {
            "type": "boolean",
            "description": "Whether to show progress indicator on this page"
        },
        "theme": {
            "type": "string",
            "description": "Visual theme for the page"
        },
        "allow_back": {
            "type": "boolean",
            "description": "Whether users can navigate back to this page"
        },
        "auto_advance": {
            "type": "boolean",
            "description": "Automatically advance to next page after completion"
        },
        "time_limit": {
            "type": "integer",
            "description": "Time limit for this page in seconds"
        }
    },
    "additionalProperties": True,
    "example": {
        "show_progress": True,
        "theme": "modern",
        "allow_back": True,
        "auto_advance": False
    }
}

# Schema for question configuration
QUESTION_CONFIG_SCHEMA = {
    "type": "object",
    "description": "Configuration options specific to question types",
    "properties": {
        "placeholder": {
            "type": "string",
            "description": "Placeholder text for input fields"
        },
        "options": {
            "type": "array",
            "description": "Available options for select/radio/checkbox questions",
            "items": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "label": {"type": "string"},
                    "disabled": {"type": "boolean", "default": False}
                },
                "required": ["value", "label"]
            }
        },
        "multiple": {
            "type": "boolean",
            "description": "Allow multiple selections"
        },
        "min_length": {
            "type": "integer",
            "description": "Minimum input length"
        },
        "max_length": {
            "type": "integer", 
            "description": "Maximum input length"
        },
        "accept": {
            "type": "string",
            "description": "Accepted file types (for file uploads)"
        },
        "max_file_size": {
            "type": "integer",
            "description": "Maximum file size in bytes"
        },
        "rows": {
            "type": "integer",
            "description": "Number of rows for textarea"
        },
        "columns": {
            "type": "integer",
            "description": "Number of columns for textarea"
        }
    },
    "additionalProperties": True,
    "example": {
        "placeholder": "Enter your email address",
        "max_length": 255,
        "options": [
            {"value": "option1", "label": "First Option"},
            {"value": "option2", "label": "Second Option"}
        ]
    }
}

# Schema for validation configuration
VALIDATION_CONFIG_SCHEMA = {
    "type": "object",
    "description": "Validation rules for question responses",
    "properties": {
        "required": {
            "type": "boolean",
            "description": "Whether this question is required"
        },
        "min_length": {
            "type": "integer",
            "description": "Minimum input length"
        },
        "max_length": {
            "type": "integer",
            "description": "Maximum input length"
        },
        "min_value": {
            "type": "number",
            "description": "Minimum numeric value"
        },
        "max_value": {
            "type": "number",
            "description": "Maximum numeric value"
        },
        "pattern": {
            "type": "string",
            "description": "Regular expression pattern for validation"
        },
        "custom_error_message": {
            "type": "string",
            "description": "Custom error message for validation failures"
        },
        "email": {
            "type": "boolean",
            "description": "Validate as email address"
        },
        "url": {
            "type": "boolean",
            "description": "Validate as URL"
        }
    },
    "additionalProperties": True,
    "example": {
        "required": True,
        "min_length": 2,
        "max_length": 100,
        "pattern": "^[a-zA-Z\\s]+$",
        "custom_error_message": "Please enter a valid name"
    }
}

# Schema for question type info in serialized data
QUESTION_TYPE_INFO_SCHEMA = {
    "type": "object",
    "description": "Question type information with rendering configuration",
    "properties": {
        "slug": {
            "type": "string",
            "description": "Question type identifier"
        },
        "name": {
            "type": "string", 
            "description": "Human-readable type name"
        },
        "config": {
            "$ref": "#/components/schemas/QuestionTypeConfig",
            "description": "Type-specific configuration for rendering"
        }
    },
    "required": ["slug", "name", "config"],
    "example": {
        "slug": "address",
        "name": "Address",
        "config": {
            "fields": [
                {"name": "street", "label": "Street Address", "type": "text", "required": True},
                {"name": "city", "label": "City", "type": "text", "required": True},
                {"name": "state", "label": "State", "type": "select", "required": True},
                {"name": "zip", "label": "ZIP Code", "type": "text", "required": True}
            ],
            "layout": "stacked",
            "country_support": ["US", "CA"]
        }
    }
}

# Schema for question type configuration (different from question config)
QUESTION_TYPE_CONFIG_SCHEMA = {
    "type": "object",
    "description": "Configuration that defines how a question type should be rendered",
    "properties": {
        "fields": {
            "type": "array",
            "description": "Sub-fields for complex question types",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Field identifier"},
                    "label": {"type": "string", "description": "Field display label"},
                    "type": {"type": "string", "description": "Field input type"},
                    "required": {"type": "boolean", "description": "Whether field is required"},
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "value": {"type": "string"},
                                "label": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "layout": {
            "type": "string",
            "enum": ["inline", "stacked", "grid"],
            "description": "How to lay out multiple fields"
        },
        "validation_rules": {
            "type": "object",
            "description": "Default validation rules for this type"
        },
        "input_component": {
            "type": "string", 
            "description": "Vue component name to use for rendering"
        }
    },
    "additionalProperties": True,
    "example": {
        "fields": [
            {"name": "first_name", "label": "First Name", "type": "text", "required": True},
            {"name": "last_name", "label": "Last Name", "type": "text", "required": True}
        ],
        "layout": "inline",
        "input_component": "NameInput"
    }
}

# Schema for serialized question in form versions
SERIALIZED_QUESTION_SCHEMA = {
    "type": "object",
    "description": "Complete question data as stored in form versions",
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique question identifier"
        },
        "type": {
            "$ref": "#/components/schemas/QuestionTypeInfo",
            "description": "Question type information with rendering config"
        },
        "name": {
            "type": "string",
            "description": "Internal question name"
        },
        "slug": {
            "type": "string",
            "description": "URL-friendly question identifier"
        },
        "text": {
            "type": "string",
            "description": "Question text displayed to users"
        },
        "subtext": {
            "type": ["string", "null"],
            "description": "Additional help text for the question"
        },
        "required": {
            "type": "boolean",
            "description": "Whether this question is required"
        },
        "config": {
            "$ref": "#/components/schemas/QuestionConfig",
            "description": "Question-specific configuration"
        },
        "validation": {
            "$ref": "#/components/schemas/ValidationConfig",
            "description": "Validation rules for this question"
        },
        "conditional_logic": {
            "$ref": "#/components/schemas/ConditionalLogic",
            "description": "Conditions for showing/hiding this question"
        },
        "order": {
            "type": "integer",
            "description": "Display order within the page"
        }
    },
    "required": ["id", "type", "name", "slug", "text", "required", "order"],
    "example": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "type": "email",
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
        "order": 1
    }
}

# Schema for serialized page in form versions
SERIALIZED_PAGE_SCHEMA = {
    "type": "object",
    "description": "Complete page data as stored in form versions",
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique page identifier"
        },
        "name": {
            "type": "string",
            "description": "Page name"
        },
        "slug": {
            "type": "string",
            "description": "URL-friendly page identifier"
        },
        "order": {
            "type": "integer",
            "description": "Page order in the form"
        },
        "conditional_logic": {
            "$ref": "#/components/schemas/ConditionalLogic",
            "description": "Conditions for showing this page"
        },
        "config": {
            "$ref": "#/components/schemas/PageConfig",
            "description": "Page-specific configuration"
        },
        "questions": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/SerializedQuestion"},
            "description": "Questions on this page"
        }
    },
    "required": ["id", "name", "slug", "order", "questions"],
    "example": {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "name": "Contact Information",
        "slug": "contact-info",
        "order": 1,
        "conditional_logic": {},
        "config": {
            "show_progress": True,
            "theme": "default"
        },
        "questions": [
            # Would contain SerializedQuestion objects
        ]
    }
}

# Schema for complete serialized form data
SERIALIZED_FORM_DATA_SCHEMA = {
    "type": "object",
    "description": "Complete form structure as stored in form versions",
    "properties": {
        "form_id": {
            "type": "string", 
            "format": "uuid",
            "description": "Original form identifier"
        },
        "name": {
            "type": "string",
            "description": "Form name"
        },
        "slug": {
            "type": "string",
            "description": "URL-friendly form identifier"
        },
        "pages": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/SerializedPage"},
            "description": "All pages in this form version"
        }
    },
    "required": ["form_id", "name", "slug", "pages"],
    "example": {
        "form_id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Customer Feedback Survey",
        "slug": "customer-feedback-survey",
        "pages": [
            {
                "id": "page-1",
                "name": "Basic Information",
                "slug": "basic-info",
                "order": 1,
                "conditional_logic": {},
                "config": {"show_progress": True},
                "questions": [
                    {
                        "id": "q1",
                        "type": "text",
                        "name": "Full Name",
                        "slug": "full_name",
                        "text": "What is your full name?",
                        "required": True,
                        "config": {"placeholder": "Enter your name"},
                        "validation": {"min_length": 2},
                        "conditional_logic": {},
                        "order": 1
                    }
                ]
            }
        ]
    }
}

# Schema for form submission answers
SUBMISSION_ANSWERS_SCHEMA = {
    "type": "object",
    "description": "User responses mapped by question slug",
    "additionalProperties": {
        "oneOf": [
            {"type": "string", "description": "Text response"},
            {"type": "number", "description": "Numeric response"},
            {"type": "boolean", "description": "Boolean response"},
            {
                "type": "array",
                "items": {"type": "string"},
                "description": "Multiple choice response"
            },
            {
                "type": "object",
                "description": "Complex response (file upload, etc.)"
            }
        ]
    },
    "example": {
        "full_name": "John Doe",
        "email_address": "john@example.com",
        "age": 30,
        "interests": ["technology", "sports", "music"],
        "newsletter_signup": True,
        "rating": 8,
        "comments": "Great service!"
    }
}

# Component schemas for OpenAPI specification
COMPONENT_SCHEMAS = {
    'ConditionalLogic': CONDITIONAL_LOGIC_SCHEMA,
    'PageConfig': PAGE_CONFIG_SCHEMA,
    'QuestionConfig': QUESTION_CONFIG_SCHEMA,
    'QuestionTypeConfig': QUESTION_TYPE_CONFIG_SCHEMA,
    'QuestionTypeInfo': QUESTION_TYPE_INFO_SCHEMA,
    'ValidationConfig': VALIDATION_CONFIG_SCHEMA,
    'SerializedQuestion': SERIALIZED_QUESTION_SCHEMA,
    'SerializedPage': SERIALIZED_PAGE_SCHEMA,
    'SerializedFormData': SERIALIZED_FORM_DATA_SCHEMA,
    'SubmissionAnswers': SUBMISSION_ANSWERS_SCHEMA,
}