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
                'disabled_condition': page.disabled_condition,
                'config': page.config,
                'questions': [],
                'question_groups': []
            }
            
            # Add regular questions
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
                    'disabled_condition': question.disabled_condition,
                    'order': question.order
                }
                page_data['questions'].append(question_data)
            
            # Add question groups
            for group in page.question_groups.all().order_by('order'):
                group_data = {
                    'id': str(group.id),
                    'name': group.name,
                    'slug': group.slug,
                    'display_type': group.display_type,
                    'config': group.config,
                    'order': group.order,
                    'template_slug': group.template.slug if group.template else None,
                    'questions': []
                }
                
                for question in group.questions.all().order_by('order'):
                    question_data = {
                        'id': str(question.id),
                        'type': question.type.slug,
                        'name': question.name,
                        'slug': question.slug,
                        'text': question.text,
                        'subtext': question.subtext,
                        'required': question.required,
                        'config': question.config,
                        'validation': question.validation,
                        'conditional_logic': question.conditional_logic,
                        'disabled_condition': question.disabled_condition,
                        'order': question.order
                    }
                    group_data['questions'].append(question_data)
                
                page_data['question_groups'].append(group_data)
            
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
    disabled_condition = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Condition that determines if this page should be disabled"
    )
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
    """Basic input types like short-text, number, dropdown, yes-no"""
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


class QuestionGroupTemplate(models.Model):
    """Reusable templates for creating question groups (e.g., Address, Contact Info)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    display_type = models.CharField(
        max_length=50,
        help_text="UI hint for rendering this group type",
        choices=[
            ('address', 'Address Block'),
            ('contact', 'Contact Information'),
            ('name', 'Name Fields'),
            ('date_time', 'Date and Time'),
            ('custom', 'Custom Group')
        ]
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Template configuration and default settings"
    )
    question_template = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of question definitions to create when using this template"
    )
    is_active = models.BooleanField(default=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Question Group Template"
        verbose_name_plural = "Question Group Templates"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def create_group_from_template(self, page, group_name=None, order=None):
        """Create a QuestionGroup instance from this template"""
        
        # Create the group
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        group = QuestionGroup.objects.create(
            page=page,
            template=self,
            name=group_name or self.name,
            slug=f"{self.slug}-{unique_suffix}",
            display_type=self.display_type,
            config=self.config.copy(),
            order=order or (page.question_groups.count() + 1)
        )
        
        # Create questions from template
        for i, question_def in enumerate(self.question_template):
            question_type = QuestionType.objects.get(slug=question_def['type_slug'])
            
            Question.objects.create(
                question_group=group,
                type=question_type,
                name=question_def['name'],
                slug=f"{group.slug}_{question_def['slug_suffix']}",
                text=question_def['text'],
                subtext=question_def.get('subtext', ''),
                required=question_def.get('required', False),
                config=question_def.get('config', {}),
                validation=question_def.get('validation', {}),
                conditional_logic=question_def.get('conditional_logic', {}),
                order=i + 1
            )
        
        return group

    def __str__(self):
        return self.name


class QuestionGroup(models.Model):
    """Actual instances of grouped questions on specific pages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='question_groups')
    template = models.ForeignKey(
        QuestionGroupTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='instances',
        help_text="Template this group was created from (optional)"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, blank=True)
    display_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Hint for frontend rendering",
        choices=[
            ('address', 'Address Block'),
            ('contact', 'Contact Information'),
            ('name', 'Name Fields'),
            ('date_time', 'Date and Time'),
            ('custom', 'Custom Group')
        ]
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Group-specific configuration and display settings"
    )
    order = models.IntegerField()
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']
        unique_together = [
            ['page', 'slug'],
            ['page', 'order']
        ]

    def __str__(self):
        template_info = f" (from {self.template.name})" if self.template else ""
        return f"{self.page.name} - {self.name} (Group){template_info}"


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # A question belongs to either a page directly OR to a question group
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    question_group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, blank=True)
    text = models.TextField()
    subtext = models.TextField(null=True, blank=True)
    required = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)
    validation = models.JSONField(default=dict, blank=True)
    conditional_logic = models.JSONField(default=dict, blank=True)
    disabled_condition = models.JSONField(
        default=dict,
        blank=True,
        help_text="Condition that determines if this question should be disabled"
    )
    order = models.IntegerField()
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Ensure question belongs to either page or group, not both
        if self.page and self.question_group:
            raise ValueError("Question cannot belong to both a page and a question group")
        if not self.page and not self.question_group:
            raise ValueError("Question must belong to either a page or a question group")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']
        # Unique constraint depends on whether it's in a page or group
        constraints = [
            models.UniqueConstraint(
                fields=['page', 'order'],
                condition=models.Q(page__isnull=False),
                name='unique_page_question_order'
            ),
            models.UniqueConstraint(
                fields=['question_group', 'order'],
                condition=models.Q(question_group__isnull=False),
                name='unique_group_question_order'
            )
        ]

    def __str__(self):
        if self.page:
            return f"{self.page.name} - {self.name}"
        elif self.question_group:
            return f"{self.question_group.name} - {self.name}"
        return self.name


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