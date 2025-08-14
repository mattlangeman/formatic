"""
ViewSet for managing question group templates.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.form_builder.models import QuestionGroupTemplate
from .serializers import QuestionGroupTemplateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List question group templates",
        description="Returns all active question group templates available for use",
        responses={
            200: QuestionGroupTemplateSerializer(many=True)
        }
    ),
    retrieve=extend_schema(
        summary="Get question group template",
        description="Get detailed information about a specific question group template",
        responses={
            200: QuestionGroupTemplateSerializer
        }
    )
)
class QuestionGroupTemplateViewSet(ReadOnlyModelViewSet):
    """ViewSet for listing and retrieving question group templates."""
    serializer_class = QuestionGroupTemplateSerializer
    queryset = QuestionGroupTemplate.objects.filter(is_active=True).order_by('name')
    lookup_field = 'slug'