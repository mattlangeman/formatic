"""
ViewSet for managing question groups in the form builder.
"""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from apps.form_builder.models import Page, QuestionGroup, Question, QuestionType, QuestionGroupTemplate
from .serializers import (
    QuestionGroupSerializer, CreateQuestionGroupSerializer, 
    UpdateQuestionGroupSerializer, QuestionSerializer,
    CreateQuestionSerializer, UpdateQuestionSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List question groups for a page",
        description="Returns all question groups for a specific page, ordered by group order",
        responses={
            200: QuestionGroupSerializer(many=True)
        }
    ),
    create=extend_schema(
        summary="Create new question group",
        description="Create a new question group for a page"
    ),
    update=extend_schema(
        summary="Update question group",
        description="Update question group details and configuration"
    ),
    destroy=extend_schema(
        summary="Delete question group",
        description="Delete a question group and all its questions"
    )
)
class FormBuilderQuestionGroupViewSet(ModelViewSet):
    """ViewSet for managing question groups in the form builder."""
    serializer_class = QuestionGroupSerializer
    
    def get_queryset(self):
        form_slug = self.kwargs.get('form_slug')
        page_pk = self.kwargs.get('page_pk')
        if form_slug and page_pk:
            return QuestionGroup.objects.filter(
                page__id=page_pk,
                page__form__slug=form_slug,
                page__form__is_active=True
            ).order_by('order')
        return QuestionGroup.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateQuestionGroupSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateQuestionGroupSerializer
        return QuestionGroupSerializer
    
    def create(self, request, form_slug=None, page_pk=None):
        """Create a new question group for a page"""
        page = get_object_or_404(Page, id=page_pk, form__slug=form_slug, form__is_active=True)
        
        # Get next order number
        last_group = page.question_groups.order_by('order').last()
        next_order = (last_group.order + 1) if last_group else 1
        
        # Check if creating from template
        template_slug = request.data.get('template_slug')
        if template_slug:
            try:
                template = QuestionGroupTemplate.objects.get(slug=template_slug, is_active=True)
                
                # Create group from template
                group = template.create_group_from_template(
                    page=page,
                    group_name=request.data.get('name', template.name),
                    order=next_order
                )
                
                # Return full group data with questions
                return Response(
                    QuestionGroupSerializer(group).data,
                    status=status.HTTP_201_CREATED
                )
                
            except QuestionGroupTemplate.DoesNotExist:
                return Response(
                    {'error': f'Template "{template_slug}" not found'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Regular group creation (without template)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save(page=page, order=next_order)
            
            # Return full group data with questions
            return Response(
                QuestionGroupSerializer(group).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, form_slug=None, page_pk=None, pk=None):
        """Update a question group"""
        page = get_object_or_404(Page, id=page_pk, form__slug=form_slug, form__is_active=True)
        group = get_object_or_404(QuestionGroup, id=pk, page=page)
        
        serializer = self.get_serializer(group, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            # Return full group data with questions
            return Response(
                QuestionGroupSerializer(group).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, form_slug=None, page_pk=None, pk=None):
        """Partially update a question group"""
        page = get_object_or_404(Page, id=page_pk, form__slug=form_slug, form__is_active=True)
        group = get_object_or_404(QuestionGroup, id=pk, page=page)
        
        serializer = self.get_serializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return full group data with questions
            return Response(
                QuestionGroupSerializer(group).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Reorder question groups",
        description="Update the order of question groups in a page",
        request={
            "type": "object",
            "properties": {
                "group_orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "order": {"type": "integer"}
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request, form_slug=None, page_pk=None):
        """Reorder question groups in a page"""
        page = get_object_or_404(Page, id=page_pk, form__slug=form_slug, form__is_active=True)
        group_orders = request.data.get('group_orders', [])
        
        # To avoid unique constraint violations, update in batches
        groups_to_update = []
        for group_data in group_orders:
            group_id = group_data.get('id')
            new_order = group_data.get('order')
            try:
                group = page.question_groups.get(id=group_id)
                groups_to_update.append((group, new_order))
            except QuestionGroup.DoesNotExist:
                continue
        
        # Set temporary negative orders to avoid conflicts
        for i, (group, _) in enumerate(groups_to_update):
            group.order = -(i + 1000)
            group.save()
        
        # Now set the final orders
        for group, new_order in groups_to_update:
            group.order = new_order
            group.save()
        
        return Response({'status': 'success'})
    
    @extend_schema(
        summary="Add question to group",
        description="Add a new question to this question group",
        request=CreateQuestionSerializer,
        responses={
            201: QuestionSerializer
        }
    )
    @action(detail=True, methods=['post'], url_path='questions')
    def add_question(self, request, form_slug=None, page_pk=None, pk=None):
        """Add a question to a question group"""
        page = get_object_or_404(Page, id=page_pk, form__slug=form_slug, form__is_active=True)
        group = get_object_or_404(QuestionGroup, id=pk, page=page)
        
        # Get next order number
        last_question = group.questions.order_by('order').last()
        next_order = (last_question.order + 1) if last_question else 1
        
        # Get question type
        question_type_slug = request.data.get('type_slug')
        if not question_type_slug:
            return Response({'error': 'type_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        question_type = get_object_or_404(QuestionType, slug=question_type_slug)
        
        serializer = CreateQuestionSerializer(data=request.data)
        if serializer.is_valid():
            # Create question with proper fields
            question_data = serializer.validated_data.copy()
            question_data.pop('type_slug', None)
            
            question = Question.objects.create(
                question_group=group,
                type=question_type,
                order=next_order,
                **question_data
            )
            
            # Return full question data
            return Response(
                QuestionSerializer(question).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="List questions in a group",
        description="Returns all questions in a specific question group",
        responses={
            200: QuestionSerializer(many=True)
        }
    ),
    update=extend_schema(
        summary="Update grouped question",
        description="Update a question within a group"
    ),
    destroy=extend_schema(
        summary="Delete grouped question",
        description="Delete a question from a group"
    )
)
class GroupedQuestionViewSet(ModelViewSet):
    """ViewSet for managing questions within a question group."""
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        form_slug = self.kwargs.get('form_slug')
        page_pk = self.kwargs.get('page_pk')
        group_pk = self.kwargs.get('group_pk')
        
        if form_slug and page_pk and group_pk:
            return Question.objects.filter(
                question_group__id=group_pk,
                question_group__page__id=page_pk,
                question_group__page__form__slug=form_slug,
                question_group__page__form__is_active=True
            ).order_by('order')
        return Question.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateQuestionSerializer
        return QuestionSerializer
    
    def update(self, request, form_slug=None, page_pk=None, group_pk=None, pk=None):
        """Update a question in a group"""
        question = get_object_or_404(
            Question,
            id=pk,
            question_group__id=group_pk,
            question_group__page__id=page_pk,
            question_group__page__form__slug=form_slug,
            question_group__page__form__is_active=True
        )
        
        serializer = self.get_serializer(question, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(
                QuestionSerializer(question).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, form_slug=None, page_pk=None, group_pk=None, pk=None):
        """Partially update a question in a group"""
        question = get_object_or_404(
            Question,
            id=pk,
            question_group__id=group_pk,
            question_group__page__id=page_pk,
            question_group__page__form__slug=form_slug,
            question_group__page__form__is_active=True
        )
        
        serializer = self.get_serializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                QuestionSerializer(question).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Reorder questions in group",
        description="Update the order of questions within a group",
        request={
            "type": "object",
            "properties": {
                "question_orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "order": {"type": "integer"}
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request, form_slug=None, page_pk=None, group_pk=None):
        """Reorder questions within a group"""
        group = get_object_or_404(
            QuestionGroup,
            id=group_pk,
            page__id=page_pk,
            page__form__slug=form_slug,
            page__form__is_active=True
        )
        
        question_orders = request.data.get('question_orders', [])
        
        # To avoid unique constraint violations, update in batches
        questions_to_update = []
        for question_data in question_orders:
            question_id = question_data.get('id')
            new_order = question_data.get('order')
            try:
                question = group.questions.get(id=question_id)
                questions_to_update.append((question, new_order))
            except Question.DoesNotExist:
                continue
        
        # Set temporary negative orders to avoid conflicts
        for i, (question, _) in enumerate(questions_to_update):
            question.order = -(i + 1000)
            question.save()
        
        # Now set the final orders
        for question, new_order in questions_to_update:
            question.order = new_order
            question.save()
        
        return Response({'status': 'success'})