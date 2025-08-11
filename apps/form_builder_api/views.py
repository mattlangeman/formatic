from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from apps.form_builder.models import DynamicForm, FormVersion, FormSubmission, QuestionType
from .serializers import (
    DynamicFormSerializer, FormVersionSerializer, CreateVersionSerializer,
    FormSubmissionSerializer, CreateSubmissionSerializer, UpdateSubmissionSerializer,
    QuestionTypeSerializer
)
from .schemas import SERIALIZED_FORM_DATA_SCHEMA, SUBMISSION_ANSWERS_SCHEMA


@extend_schema_view(
    list=extend_schema(
        summary="List question types",
        description="Returns all available question types with their configurations for form building",
        responses={
            200: QuestionTypeSerializer(many=True)
        }
    ),
    retrieve=extend_schema(
        summary="Get question type details",
        description="Returns detailed configuration for a specific question type",
        responses={
            200: QuestionTypeSerializer,
            404: OpenApiResponse(description="Question type not found")
        }
    )
)
class QuestionTypeViewSet(ModelViewSet):
    """ViewSet for question types and their configurations."""
    queryset = QuestionType.objects.all().order_by('name')
    serializer_class = QuestionTypeSerializer
    lookup_field = 'slug'
    http_method_names = ['get']  # Read-only for now


@extend_schema_view(
    list=extend_schema(
        summary="List active forms",
        description="Returns a list of all active dynamic forms with their current structure",
        responses={
            200: DynamicFormSerializer(many=True)
        }
    ),
    create=extend_schema(
        summary="Create new form",
        description="Create a new dynamic form with basic information"
    ),
    update=extend_schema(
        summary="Update form",
        description="Update form details (does not affect published versions)"
    ),
    destroy=extend_schema(
        summary="Deactivate form",
        description="Deactivates a form (sets is_active=False)"
    )
)
class FormViewSet(ModelViewSet):
    """ViewSet for managing dynamic forms and their structures."""
    queryset = DynamicForm.objects.filter(is_active=True)
    serializer_class = DynamicFormSerializer
    lookup_field = 'slug'

    @extend_schema(
        summary="Get published form structure",
        description="Returns the complete serialized structure of the latest published form version, ready for rendering",
        parameters=[
            OpenApiParameter(
                name='slug',
                description='Form slug identifier',
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: OpenApiResponse(
                response=SERIALIZED_FORM_DATA_SCHEMA,
                description="Complete form structure with pages and questions",
                examples=[
                    OpenApiExample(
                        'Customer Survey Structure',
                        value={
                            "form_id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Customer Survey",
                            "slug": "customer-survey",
                            "pages": [
                                {
                                    "id": "page-1",
                                    "name": "Contact Information",
                                    "slug": "contact-info",
                                    "order": 1,
                                    "questions": [
                                        {
                                            "id": "q1",
                                            "type": "email",
                                            "slug": "email_address",
                                            "text": "Email Address",
                                            "required": True,
                                            "config": {"placeholder": "your@email.com"},
                                            "validation": {"email": True}
                                        }
                                    ]
                                }
                            ]
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description="Form not found or no published version available")
        }
    )
    def retrieve(self, request, slug=None):
        """Get latest published version of a form"""
        form = get_object_or_404(DynamicForm, slug=slug, is_active=True)
        latest_version = form.get_latest_published_version()
        
        if not latest_version:
            return Response(
                {'error': 'No published version available'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(latest_version.serialized_form_data)

    @extend_schema(
        summary="Get draft form structure",
        description="Returns the current draft structure of the form (for admin/editing purposes)",
        responses={
            200: DynamicFormSerializer,
            404: OpenApiResponse(description="Form not found")
        }
    )
    @action(detail=True, methods=['get'])
    def draft(self, request, slug=None):
        """Get current draft structure (for admin)"""
        form = get_object_or_404(DynamicForm, slug=slug, is_active=True)
        serializer = self.get_serializer(form)
        return Response(serializer.data)

    @extend_schema(
        summary="List form versions",
        description="Returns all versions of a form, ordered by version number (newest first)",
        responses={
            200: FormVersionSerializer(many=True),
            404: OpenApiResponse(description="Form not found")
        }
    )
    @action(detail=True, methods=['get'])
    def versions(self, request, slug=None):
        """List all versions of a form"""
        form = get_object_or_404(DynamicForm, slug=slug, is_active=True)
        versions = form.versions.all()
        serializer = FormVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create form version",
        description="Creates a new version from the current form structure. Optionally publish immediately.",
        request=CreateVersionSerializer,
        responses={
            201: FormVersionSerializer,
            400: OpenApiResponse(description="Invalid request data"),
            404: OpenApiResponse(description="Form not found")
        },
        examples=[
            OpenApiExample(
                'Create and publish version',
                request_only=True,
                value={
                    "notes": "Updated validation rules and added new questions",
                    "created_by": "admin@example.com",
                    "is_published": True
                }
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='create-version')
    def create_version(self, request, slug=None):
        """Create a new version from current form structure"""
        form = get_object_or_404(DynamicForm, slug=slug, is_active=True)
        serializer = CreateVersionSerializer(data=request.data)
        
        if serializer.is_valid():
            version = form.create_version(
                notes=serializer.validated_data.get('notes', ''),
                created_by=serializer.validated_data.get('created_by', '')
            )
            
            # Publish if requested
            if serializer.validated_data.get('is_published', False):
                version.is_published = True
                version.save()
            
            return Response(
                FormVersionSerializer(version).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="List form versions",
        description="Returns all versions for a specific form"
    )
)
class FormVersionViewSet(ModelViewSet):
    """ViewSet for managing individual form versions."""
    serializer_class = FormVersionSerializer
    
    def get_queryset(self):
        form_slug = self.kwargs.get('form_slug')
        if form_slug:
            return FormVersion.objects.filter(form__slug=form_slug)
        return FormVersion.objects.none()

    @extend_schema(
        summary="Get specific form version",
        description="Returns the serialized form data for a specific version number",
        responses={
            200: OpenApiResponse(
                response=SERIALIZED_FORM_DATA_SCHEMA,
                description="Complete form structure for this version"
            ),
            404: OpenApiResponse(description="Form or version not found")
        }
    )
    def retrieve(self, request, form_slug=None, pk=None):
        """Get specific version by version number"""
        form = get_object_or_404(DynamicForm, slug=form_slug, is_active=True)
        version = get_object_or_404(form.versions, version_number=pk)
        return Response(version.serialized_form_data)

    @extend_schema(
        summary="Publish form version",
        description="Marks a specific version as published, making it available for form rendering",
        responses={
            200: FormVersionSerializer,
            404: OpenApiResponse(description="Form or version not found")
        }
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, form_slug=None, pk=None):
        """Publish a specific version"""
        form = get_object_or_404(DynamicForm, slug=form_slug, is_active=True)
        version = get_object_or_404(form.versions, version_number=pk)
        
        version.is_published = True
        version.save()
        
        return Response(
            FormVersionSerializer(version).data,
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(
        summary="List submissions",
        description="Returns all form submissions with pagination support"
    )
)
class FormSubmissionViewSet(ModelViewSet):
    """ViewSet for managing form submissions and responses."""
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    
    def get_queryset(self):
        """Filter submissions by query parameters"""
        queryset = super().get_queryset()
        
        # Filter by user session ID
        user_session_id = self.request.query_params.get('user_session_id')
        if user_session_id:
            queryset = queryset.filter(user_session_id=user_session_id)
        
        # Filter by form slug
        form_slug = self.request.query_params.get('form_slug')
        if form_slug:
            queryset = queryset.filter(form_version__form__slug=form_slug)
            
        return queryset.order_by('-created_datetime')

    @extend_schema(
        summary="Create form submission",
        description="Creates a new form submission using the latest published version of the specified form",
        request=CreateSubmissionSerializer,
        responses={
            201: FormSubmissionSerializer,
            400: OpenApiResponse(description="Invalid request data"),
            404: OpenApiResponse(description="Form not found or no published version")
        },
        examples=[
            OpenApiExample(
                'Create submission',
                request_only=True,
                value={
                    "form_slug": "customer-survey",
                    "user_session_id": "sess_abc123",
                    "user_email": "user@example.com"
                }
            )
        ]
    )
    def create(self, request):
        """Create a new submission using latest published version"""
        serializer = CreateSubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
            form_slug = serializer.validated_data['form_slug']
            form = get_object_or_404(DynamicForm, slug=form_slug, is_active=True)
            latest_version = form.get_latest_published_version()
            
            if not latest_version:
                return Response(
                    {'error': 'No published version available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get client IP
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            submission = FormSubmission.objects.create(
                form_version=latest_version,
                user_session_id=serializer.validated_data.get('user_session_id'),
                user_email=serializer.validated_data.get('user_email'),
                ip_address=ip_address
            )
            
            return Response(
                FormSubmissionSerializer(submission).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update submission answers",
        description="Updates the answers for a form submission. Can also mark submission as complete.",
        request=UpdateSubmissionSerializer,
        responses={
            200: FormSubmissionSerializer,
            400: OpenApiResponse(description="Invalid request data"),
            404: OpenApiResponse(description="Submission not found")
        },
        examples=[
            OpenApiExample(
                'Update answers',
                request_only=True,
                value={
                    "answers": {
                        "full_name": "John Doe",
                        "email_address": "john@example.com",
                        "rating": 8
                    },
                    "is_complete": False
                }
            )
        ]
    )
    def update(self, request, pk=None, partial=False):
        """Update submission answers"""
        submission = get_object_or_404(FormSubmission, pk=pk)
        serializer = UpdateSubmissionSerializer(data=request.data, partial=partial)
        
        if serializer.is_valid():
            # Update answers by merging with existing data
            if 'answers' in serializer.validated_data:
                submission.answers.update(serializer.validated_data['answers'])
            
            if 'is_complete' in serializer.validated_data:
                submission.is_complete = serializer.validated_data['is_complete']
            
            if submission.is_complete and not submission.completed_datetime:
                submission.completed_datetime = timezone.now()
            
            submission.save()
            
            return Response(
                FormSubmissionSerializer(submission).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """Partial update submission answers"""
        return self.update(request, pk=pk, partial=True)

    @extend_schema(
        summary="Mark submission complete",
        description="Marks a submission as complete and sets the completion timestamp",
        responses={
            200: FormSubmissionSerializer,
            404: OpenApiResponse(description="Submission not found")
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark submission as complete"""
        submission = get_object_or_404(FormSubmission, pk=pk)
        
        if not submission.is_complete:
            submission.is_complete = True
            submission.completed_datetime = timezone.now()
            submission.save()
        
        return Response(
            FormSubmissionSerializer(submission).data,
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Get CSRF token",
    description="Returns a CSRF token for use with form submissions",
    responses={
        200: OpenApiResponse(
            description="CSRF token",
            examples=[
                OpenApiExample(
                    'CSRF Token Response',
                    value={
                        "csrfToken": "abc123xyz789"
                    }
                )
            ]
        )
    }
)
@api_view(['GET'])
@ensure_csrf_cookie
def csrf_token_view(request):
    """Get CSRF token for frontend"""
    return Response({
        'csrfToken': get_token(request)
    })
