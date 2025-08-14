from django.core.management.base import BaseCommand
from django.db import transaction
from apps.form_builder.models import QuestionType, QuestionGroupTemplate, QuestionGroup, Question


class Command(BaseCommand):
    help = 'Migrate Address from QuestionType to QuestionGroupTemplate'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Step 1: Create Address QuestionGroupTemplate
            self.stdout.write('Creating Address QuestionGroupTemplate...')
            
            address_template, created = QuestionGroupTemplate.objects.get_or_create(
                slug='address',
                defaults={
                    'name': 'Address',
                    'description': 'Complete address information including street, city, state/province, and postal code',
                    'display_type': 'address',
                    'config': {
                        'layout': 'stacked',
                        'show_labels': True,
                        'validation': {
                            'required_fields': ['street', 'city', 'country']
                        }
                    },
                    'question_template': [
                        {
                            'type_slug': 'short-text',
                            'name': 'Street Address',
                            'slug_suffix': 'street',
                            'text': 'Street Address',
                            'subtext': 'Enter your full street address',
                            'required': True,
                            'config': {
                                'placeholder': '123 Main Street'
                            },
                            'validation': {},
                            'conditional_logic': {}
                        },
                        {
                            'type_slug': 'short-text',
                            'name': 'City',
                            'slug_suffix': 'city',
                            'text': 'City',
                            'subtext': '',
                            'required': True,
                            'config': {
                                'placeholder': 'Enter city name'
                            },
                            'validation': {},
                            'conditional_logic': {}
                        },
                        {
                            'type_slug': 'dropdown',
                            'name': 'Country',
                            'slug_suffix': 'country',
                            'text': 'Country',
                            'subtext': '',
                            'required': True,
                            'config': {
                                'options': [
                                    {'value': 'US', 'label': 'United States'},
                                    {'value': 'CA', 'label': 'Canada'},
                                    {'value': 'MX', 'label': 'Mexico'},
                                    {'value': 'UK', 'label': 'United Kingdom'},
                                    {'value': 'DE', 'label': 'Germany'},
                                    {'value': 'FR', 'label': 'France'},
                                    {'value': 'IT', 'label': 'Italy'},
                                    {'value': 'ES', 'label': 'Spain'},
                                    {'value': 'AU', 'label': 'Australia'},
                                    {'value': 'JP', 'label': 'Japan'}
                                ]
                            },
                            'validation': {},
                            'conditional_logic': {}
                        },
                        {
                            'type_slug': 'dropdown',
                            'name': 'State/Province',
                            'slug_suffix': 'state',
                            'text': 'State/Province',
                            'subtext': '',
                            'required': False,
                            'config': {
                                'options': [
                                    {'value': 'AL', 'label': 'Alabama'},
                                    {'value': 'AK', 'label': 'Alaska'},
                                    {'value': 'AZ', 'label': 'Arizona'},
                                    {'value': 'AR', 'label': 'Arkansas'},
                                    {'value': 'CA', 'label': 'California'},
                                    {'value': 'CO', 'label': 'Colorado'},
                                    {'value': 'CT', 'label': 'Connecticut'},
                                    {'value': 'DE', 'label': 'Delaware'},
                                    {'value': 'FL', 'label': 'Florida'},
                                    {'value': 'GA', 'label': 'Georgia'},
                                    {'value': 'HI', 'label': 'Hawaii'},
                                    {'value': 'ID', 'label': 'Idaho'},
                                    {'value': 'IL', 'label': 'Illinois'},
                                    {'value': 'IN', 'label': 'Indiana'},
                                    {'value': 'IA', 'label': 'Iowa'},
                                    {'value': 'KS', 'label': 'Kansas'},
                                    {'value': 'KY', 'label': 'Kentucky'},
                                    {'value': 'LA', 'label': 'Louisiana'},
                                    {'value': 'ME', 'label': 'Maine'},
                                    {'value': 'MD', 'label': 'Maryland'},
                                    {'value': 'MA', 'label': 'Massachusetts'},
                                    {'value': 'MI', 'label': 'Michigan'},
                                    {'value': 'MN', 'label': 'Minnesota'},
                                    {'value': 'MS', 'label': 'Mississippi'},
                                    {'value': 'MO', 'label': 'Missouri'},
                                    {'value': 'MT', 'label': 'Montana'},
                                    {'value': 'NE', 'label': 'Nebraska'},
                                    {'value': 'NV', 'label': 'Nevada'},
                                    {'value': 'NH', 'label': 'New Hampshire'},
                                    {'value': 'NJ', 'label': 'New Jersey'},
                                    {'value': 'NM', 'label': 'New Mexico'},
                                    {'value': 'NY', 'label': 'New York'},
                                    {'value': 'NC', 'label': 'North Carolina'},
                                    {'value': 'ND', 'label': 'North Dakota'},
                                    {'value': 'OH', 'label': 'Ohio'},
                                    {'value': 'OK', 'label': 'Oklahoma'},
                                    {'value': 'OR', 'label': 'Oregon'},
                                    {'value': 'PA', 'label': 'Pennsylvania'},
                                    {'value': 'RI', 'label': 'Rhode Island'},
                                    {'value': 'SC', 'label': 'South Carolina'},
                                    {'value': 'SD', 'label': 'South Dakota'},
                                    {'value': 'TN', 'label': 'Tennessee'},
                                    {'value': 'TX', 'label': 'Texas'},
                                    {'value': 'UT', 'label': 'Utah'},
                                    {'value': 'VT', 'label': 'Vermont'},
                                    {'value': 'VA', 'label': 'Virginia'},
                                    {'value': 'WA', 'label': 'Washington'},
                                    {'value': 'WV', 'label': 'West Virginia'},
                                    {'value': 'WI', 'label': 'Wisconsin'},
                                    {'value': 'WY', 'label': 'Wyoming'},
                                    # Canadian provinces
                                    {'value': 'AB', 'label': 'Alberta'},
                                    {'value': 'BC', 'label': 'British Columbia'},
                                    {'value': 'MB', 'label': 'Manitoba'},
                                    {'value': 'NB', 'label': 'New Brunswick'},
                                    {'value': 'NL', 'label': 'Newfoundland and Labrador'},
                                    {'value': 'NS', 'label': 'Nova Scotia'},
                                    {'value': 'ON', 'label': 'Ontario'},
                                    {'value': 'PE', 'label': 'Prince Edward Island'},
                                    {'value': 'QC', 'label': 'Quebec'},
                                    {'value': 'SK', 'label': 'Saskatchewan'},
                                    {'value': 'NT', 'label': 'Northwest Territories'},
                                    {'value': 'NU', 'label': 'Nunavut'},
                                    {'value': 'YT', 'label': 'Yukon'}
                                ]
                            },
                            'validation': {},
                            'conditional_logic': {
                                'rules': [
                                    {
                                        'conditions': [
                                            {
                                                'question_slug': 'country',
                                                'operator': 'in',
                                                'value': ['US', 'CA']
                                            }
                                        ],
                                        'logical_operator': 'AND',
                                        'actions': [
                                            {
                                                'type': 'show',
                                                'target_slug': 'state'
                                            },
                                            {
                                                'type': 'set_required',
                                                'target_slug': 'state',
                                                'value': True
                                            }
                                        ]
                                    }
                                ]
                            }
                        },
                        {
                            'type_slug': 'short-text',
                            'name': 'Postal Code',
                            'slug_suffix': 'postal_code',
                            'text': 'Postal Code',
                            'subtext': '',
                            'required': False,
                            'config': {
                                'placeholder': 'Enter postal/zip code'
                            },
                            'validation': {},
                            'conditional_logic': {}
                        }
                    ],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Address QuestionGroupTemplate: {address_template.id}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Address QuestionGroupTemplate already exists: {address_template.id}')
                )

            # Step 2: Update existing QuestionGroups to reference the template
            self.stdout.write('Updating existing Address QuestionGroups...')
            
            address_groups = QuestionGroup.objects.filter(display_type='address', template__isnull=True)
            updated_count = 0
            
            for group in address_groups:
                group.template = address_template
                group.save()
                updated_count += 1
                self.stdout.write(f'  Updated group: {group.name} (ID: {group.id})')
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated {updated_count} existing Address QuestionGroups')
            )

            # Step 3: Remove Address QuestionType (optional - keeping for now to avoid breaking things)
            self.stdout.write('Checking Address QuestionType...')
            
            try:
                address_question_type = QuestionType.objects.get(slug='address')
                
                # Check if any questions are still using this type
                questions_using_address = Question.objects.filter(type=address_question_type).count()
                
                if questions_using_address > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Address QuestionType still has {questions_using_address} questions using it. '
                            'Not removing to avoid data loss. '
                            'You should manually convert these to question groups.'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Address QuestionType has no dependent questions. '
                            'You can safely remove it manually if desired.'
                        )
                    )
                    
            except QuestionType.DoesNotExist:
                self.stdout.write(
                    self.style.SUCCESS('Address QuestionType does not exist - nothing to remove.')
                )

            # Step 4: Create other common templates
            self.stdout.write('Creating other common QuestionGroupTemplates...')
            
            contact_template, created = QuestionGroupTemplate.objects.get_or_create(
                slug='contact',
                defaults={
                    'name': 'Contact Information',
                    'description': 'Email, phone, and other contact details',
                    'display_type': 'contact',
                    'config': {},
                    'question_template': [
                        {
                            'type_slug': 'short-text',
                            'name': 'Email Address',
                            'slug_suffix': 'email',
                            'text': 'Email Address',
                            'subtext': '',
                            'required': True,
                            'config': {'type': 'email'},
                            'validation': {'email': True},
                            'conditional_logic': {}
                        },
                        {
                            'type_slug': 'short-text',
                            'name': 'Phone Number',
                            'slug_suffix': 'phone',
                            'text': 'Phone Number',
                            'subtext': '',
                            'required': False,
                            'config': {'type': 'tel'},
                            'validation': {},
                            'conditional_logic': {}
                        }
                    ],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Contact QuestionGroupTemplate: {contact_template.id}')
                )

            name_template, created = QuestionGroupTemplate.objects.get_or_create(
                slug='name',
                defaults={
                    'name': 'Name Fields',
                    'description': 'First name, last name, and optional title',
                    'display_type': 'name',
                    'config': {},
                    'question_template': [
                        {
                            'type_slug': 'short-text',
                            'name': 'First Name',
                            'slug_suffix': 'first',
                            'text': 'First Name',
                            'subtext': '',
                            'required': True,
                            'config': {},
                            'validation': {},
                            'conditional_logic': {}
                        },
                        {
                            'type_slug': 'short-text',
                            'name': 'Last Name',
                            'slug_suffix': 'last',
                            'text': 'Last Name',
                            'subtext': '',
                            'required': True,
                            'config': {},
                            'validation': {},
                            'conditional_logic': {}
                        }
                    ],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Name QuestionGroupTemplate: {name_template.id}')
                )

            self.stdout.write(
                self.style.SUCCESS('\n✅ Address migration to QuestionGroupTemplate complete!')
            )
            self.stdout.write(
                'Next steps:'
            )
            self.stdout.write('1. Update API endpoints to use templates when creating groups')
            self.stdout.write('2. Update Vue components to use template-based group creation')
            self.stdout.write('3. Test the new template system')