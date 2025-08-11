from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormViewSet, FormVersionViewSet, FormSubmissionViewSet, QuestionTypeViewSet, csrf_token_view

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='form')
router.register(r'question-types', QuestionTypeViewSet, basename='questiontype')
router.register(r'submissions', FormSubmissionViewSet, basename='submission')

# Custom nested routes for form versions
urlpatterns = [
    path('', include(router.urls)),
    path('csrf/', csrf_token_view, name='csrf-token'),
    path('forms/<str:form_slug>/versions/', FormVersionViewSet.as_view({
        'get': 'list'
    }), name='form-versions'),
    path('forms/<str:form_slug>/versions/<int:pk>/', FormVersionViewSet.as_view({
        'get': 'retrieve'
    }), name='form-version-detail'),
    path('forms/<str:form_slug>/versions/<int:pk>/publish/', FormVersionViewSet.as_view({
        'post': 'publish'
    }), name='form-version-publish'),
]