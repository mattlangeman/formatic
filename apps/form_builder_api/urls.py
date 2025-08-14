from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FormViewSet, FormVersionViewSet, FormSubmissionViewSet, QuestionTypeViewSet,
    FormBuilderFormViewSet, FormBuilderPageViewSet, FormBuilderQuestionViewSet,
    csrf_token_view
)
from .views_questiongroup import FormBuilderQuestionGroupViewSet, GroupedQuestionViewSet
from .views_questiongroup_templates import QuestionGroupTemplateViewSet

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='form')
router.register(r'question-types', QuestionTypeViewSet, basename='questiontype')
router.register(r'question-group-templates', QuestionGroupTemplateViewSet, basename='questiongrouptemplate')
router.register(r'submissions', FormSubmissionViewSet, basename='submission')

# Form builder routes
router.register(r'builder/forms', FormBuilderFormViewSet, basename='builder-form')

# Custom nested routes for form versions and form builder
urlpatterns = [
    path('', include(router.urls)),
    path('csrf/', csrf_token_view, name='csrf-token'),
    
    # Form versions
    path('forms/<str:form_slug>/versions/', FormVersionViewSet.as_view({
        'get': 'list'
    }), name='form-versions'),
    path('forms/<str:form_slug>/versions/<int:pk>/', FormVersionViewSet.as_view({
        'get': 'retrieve'
    }), name='form-version-detail'),
    path('forms/<str:form_slug>/versions/<int:pk>/publish/', FormVersionViewSet.as_view({
        'post': 'publish'
    }), name='form-version-publish'),
    
    # Form builder - Pages
    path('builder/forms/<str:form_slug>/pages/', FormBuilderPageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='builder-pages'),
    path('builder/forms/<str:form_slug>/pages/<uuid:pk>/', FormBuilderPageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='builder-page-detail'),
    path('builder/forms/<str:form_slug>/pages/reorder/', FormBuilderPageViewSet.as_view({
        'post': 'reorder'
    }), name='builder-pages-reorder'),
    
    # Form builder - Questions
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/questions/', FormBuilderQuestionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='builder-questions'),
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/questions/<uuid:pk>/', FormBuilderQuestionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='builder-question-detail'),
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/questions/reorder/', FormBuilderQuestionViewSet.as_view({
        'post': 'reorder'
    }), name='builder-questions-reorder'),
    
    # Form builder - Question Groups
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/groups/', FormBuilderQuestionGroupViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='builder-question-groups'),
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/groups/<uuid:pk>/', FormBuilderQuestionGroupViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='builder-question-group-detail'),
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/groups/reorder/', FormBuilderQuestionGroupViewSet.as_view({
        'post': 'reorder'
    }), name='builder-question-groups-reorder'),
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/groups/<uuid:pk>/questions/', FormBuilderQuestionGroupViewSet.as_view({
        'post': 'add_question'
    }), name='builder-question-group-add-question'),
    
    # Form builder - Questions in Groups
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/groups/<uuid:group_pk>/questions/', GroupedQuestionViewSet.as_view({
        'get': 'list'
    }), name='builder-grouped-questions'),
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/groups/<uuid:group_pk>/questions/<uuid:pk>/', GroupedQuestionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='builder-grouped-question-detail'),
    path('builder/forms/<str:form_slug>/pages/<uuid:page_pk>/groups/<uuid:group_pk>/questions/reorder/', GroupedQuestionViewSet.as_view({
        'post': 'reorder'
    }), name='builder-grouped-questions-reorder'),
]