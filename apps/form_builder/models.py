import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class DynamicForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dynamic Form"
        verbose_name_plural = "Dynamic Forms"
        ordering = ['-created_datetime']

    def get_latest_published_version(self):
        """Get the latest published version of this form"""
        return self.versions.filter(is_published=True).first()

    def get_current_version_number(self):
        """Get the next version number for this form"""
        latest = self.versions.first()
        return (latest.version_number + 1) if latest else 1

    def create_version(self, notes="", created_by=""):
        """Create a new version from current form structure"""
        form_data = {
            'form_id': str(self.id),
            'name': self.name,
            'slug': self.slug,
            'pages': []
        }
        
        for page in self.pages.all().order_by('order'):
            page_data = {
                'id': str(page.id),
                'name': page.name,
                'slug': page.slug,
                'order': page.order,
                'conditional_logic': page.conditional_logic,
                'config': page.config,
                'questions': []
            }
            
            for question in page.questions.all().order_by('order'):
                question_data = {
                    'id': str(question.id),
                    'type': question.type.slug,  # Just store the slug, not the full config
                    'name': question.name,
                    'slug': question.slug,
                    'text': question.text,
                    'subtext': question.subtext,
                    'required': question.required,
                    'config': question.config,
                    'validation': question.validation,
                    'conditional_logic': question.conditional_logic,
                    'order': question.order
                }
                page_data['questions'].append(question_data)
            
            form_data['pages'].append(page_data)
        
        version = FormVersion.objects.create(
            form=self,
            version_number=self.get_current_version_number(),
            serialized_form_data=form_data,
            notes=notes,
            created_by=created_by
        )
        
        return version

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FormVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    serialized_form_data = models.JSONField()
    is_published = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Form Version"
        verbose_name_plural = "Form Versions"
        unique_together = ['form', 'version_number']
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.form.name} v{self.version_number}"


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='pages')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, blank=True)
    order = models.IntegerField()
    conditional_logic = models.JSONField(default=dict, blank=True)
    config = models.JSONField(default=dict, blank=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']
        unique_together = [
            ['form', 'order'],
            ['form', 'slug']
        ]

    def __str__(self):
        return f"{self.form.name} - {self.name}"


class QuestionType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    config = models.JSONField(default=dict, blank=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Question Type"
        verbose_name_plural = "Question Types"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='questions')
    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, blank=True)
    text = models.TextField()
    subtext = models.TextField(null=True, blank=True)
    required = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)
    validation = models.JSONField(default=dict, blank=True)
    conditional_logic = models.JSONField(default=dict, blank=True)
    order = models.IntegerField()
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['page', 'order']
        unique_together = [
            ['page', 'order']
        ]

    def __str__(self):
        return f"{self.page.name} - {self.name}"


class FormSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form_version = models.ForeignKey(FormVersion, on_delete=models.CASCADE, related_name='submissions')
    answers = models.JSONField(default=dict, blank=True)
    user_session_id = models.CharField(max_length=255, null=True, blank=True)
    user_email = models.EmailField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    started_datetime = models.DateTimeField(default=timezone.now)
    completed_datetime = models.DateTimeField(null=True, blank=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Form Submission"
        verbose_name_plural = "Form Submissions"
        ordering = ['-created_datetime']

    def __str__(self):
        status = "Complete" if self.is_complete else "In Progress"
        return f"{self.form_version.form.name} v{self.form_version.version_number} - {status} ({self.created_datetime.strftime('%Y-%m-%d %H:%M')})"


