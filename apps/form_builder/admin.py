from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import DynamicForm, Page, QuestionType, Question, FormVersion, FormSubmission


class FormVersionInline(admin.TabularInline):
    model = FormVersion
    extra = 0
    fields = ['version_number', 'is_published', 'notes', 'created_by', 'created_datetime']
    readonly_fields = ['version_number', 'created_datetime']
    ordering = ['-version_number']
    can_delete = False


@admin.register(DynamicForm)
class DynamicFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'version_count', 'latest_version', 'created_datetime', 'modified_datetime']
    list_filter = ['is_active', 'created_datetime', 'modified_datetime']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'created_datetime', 'modified_datetime']
    inlines = [FormVersionInline]
    
    def version_count(self, obj):
        return obj.versions.count()
    version_count.short_description = 'Versions'
    
    def latest_version(self, obj):
        latest = obj.versions.first()
        if latest:
            status = "Published" if latest.is_published else "Draft"
            return f"v{latest.version_number} ({status})"
        return "No versions"
    latest_version.short_description = 'Latest Version'


@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_datetime']
    list_filter = ['created_datetime']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_datetime', 'modified_datetime']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['name', 'type', 'text', 'required', 'order']
    readonly_fields = ['id']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'form', 'order', 'slug', 'created_datetime']
    list_filter = ['form', 'created_datetime']
    search_fields = ['name', 'form__name']
    readonly_fields = ['id', 'created_datetime', 'modified_datetime']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'page', 'type', 'required', 'order']
    list_filter = ['type', 'required', 'page__form']
    search_fields = ['name', 'text', 'page__name']
    readonly_fields = ['id', 'created_datetime', 'modified_datetime']


@admin.register(FormVersion)
class FormVersionAdmin(admin.ModelAdmin):
    list_display = ['form_name', 'version_number', 'is_published', 'created_by', 'created_datetime', 'view_data']
    list_filter = ['is_published', 'created_datetime', 'form']
    search_fields = ['form__name', 'notes', 'created_by']
    readonly_fields = ['id', 'version_number', 'created_datetime', 'serialized_form_data_display']
    
    def form_name(self, obj):
        return obj.form.name
    form_name.short_description = 'Form'
    form_name.admin_order_field = 'form__name'
    
    def view_data(self, obj):
        return format_html(
            '<a href="#" onclick="toggleFormData(\'form-data-{}\'); return false;">View Structure</a>'
            '<div id="form-data-{}" style="display:none; margin-top:10px; max-height:200px; overflow:auto; background:#f8f8f8; padding:10px; border:1px solid #ddd;">'
            '<pre>{}</pre></div>',
            obj.id, obj.id, str(obj.serialized_form_data)[:500] + ('...' if len(str(obj.serialized_form_data)) > 500 else '')
        )
    view_data.short_description = 'Form Data'
    view_data.allow_tags = True
    
    def serialized_form_data_display(self, obj):
        import json
        try:
            formatted_json = json.dumps(obj.serialized_form_data, indent=2)
            return format_html('<pre style="max-height: 400px; overflow: auto;">{}</pre>', formatted_json)
        except:
            return str(obj.serialized_form_data)
    serialized_form_data_display.short_description = 'Serialized Form Data'
    
    class Media:
        js = ('admin/js/form_version_admin.js',)


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form_name', 'version_number', 'user_email', 'is_complete', 'started_datetime', 'completed_datetime']
    list_filter = ['is_complete', 'form_version__form', 'started_datetime', 'completed_datetime']
    search_fields = ['user_email', 'user_session_id', 'form_version__form__name']
    readonly_fields = ['id', 'form_version', 'ip_address', 'started_datetime', 'completed_datetime', 'created_datetime', 'modified_datetime', 'answers_display']
    
    def form_name(self, obj):
        return obj.form_version.form.name
    form_name.short_description = 'Form'
    form_name.admin_order_field = 'form_version__form__name'
    
    def version_number(self, obj):
        return f"v{obj.form_version.version_number}"
    version_number.short_description = 'Version'
    version_number.admin_order_field = 'form_version__version_number'
    
    def answers_display(self, obj):
        import json
        try:
            formatted_json = json.dumps(obj.answers, indent=2)
            return format_html('<pre style="max-height: 400px; overflow: auto;">{}</pre>', formatted_json)
        except:
            return str(obj.answers)
    answers_display.short_description = 'User Answers'
