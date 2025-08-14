"""
Management command to convert Address question type to question groups.
Usage: python manage.py convert_address_to_group
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.form_builder.models import Question, QuestionType, QuestionGroup


class Command(BaseCommand):
    help = 'Convert existing Address questions to question groups'

    def handle(self, *args, **options):
        # Find all address questions
        address_type = QuestionType.objects.filter(slug='address').first()
        if not address_type:
            self.stdout.write(self.style.WARNING('No address question type found'))
            return

        address_questions = Question.objects.filter(type=address_type, page__isnull=False)
        
        if not address_questions.exists():
            self.stdout.write(self.style.WARNING('No address questions found to convert'))
            return
        
        self.stdout.write(f'Found {address_questions.count()} address questions to convert')
        
        with transaction.atomic():
            for address_q in address_questions:
                self.convert_address_question(address_q)
        
        self.stdout.write(self.style.SUCCESS('Successfully converted all address questions to groups'))
    
    def convert_address_question(self, address_q):
        """Convert a single address question to a question group"""
        page = address_q.page
        
        # Create the question group
        group = QuestionGroup.objects.create(
            page=page,
            name=address_q.name,
            slug=address_q.slug,
            display_type='address',
            config={
                'layout': 'address_block',
                'original_question_id': str(address_q.id)
            },
            order=address_q.order
        )
        
        # Get or create basic question types
        text_type, _ = QuestionType.objects.get_or_create(
            slug='short-text',
            defaults={'name': 'Short Text', 'description': 'Single line text input'}
        )
        dropdown_type, _ = QuestionType.objects.get_or_create(
            slug='dropdown',
            defaults={'name': 'Dropdown', 'description': 'Dropdown selection'}
        )
        
        # Create street address question
        Question.objects.create(
            question_group=group,
            type=text_type,
            name='Street Address',
            slug=f'{address_q.slug}_street',
            text='Street Address',
            order=1,
            required=address_q.required,
            config={'placeholder': '123 Main Street'}
        )
        
        # Create city question
        Question.objects.create(
            question_group=group,
            type=text_type,
            name='City',
            slug=f'{address_q.slug}_city',
            text='City',
            order=2,
            required=address_q.required,
            config={'placeholder': 'City'}
        )
        
        # Create country question
        country_q = Question.objects.create(
            question_group=group,
            type=dropdown_type,
            name='Country',
            slug=f'{address_q.slug}_country',
            text='Country',
            order=3,
            required=address_q.required,
            config={
                'options': {
                    'en': [
                        {'value': 'US', 'label': 'United States'},
                        {'value': 'CA', 'label': 'Canada'},
                        {'value': 'MX', 'label': 'Mexico'}
                    ]
                },
                'placeholder': 'Select country'
            }
        )
        
        # Create state/province question with conditional logic
        state_q = Question.objects.create(
            question_group=group,
            type=dropdown_type,
            name='State/Province',
            slug=f'{address_q.slug}_state',
            text='State/Province',
            order=4,
            required=False,  # Will be conditionally required
            config={
                'placeholder': 'Select state/province',
                'options': {'en': []}  # Options will be set by conditional logic
            },
            conditional_logic={
                'rules': [
                    {
                        'id': 'us_states',
                        'conditions': [
                            {
                                'question_slug': f'{address_q.slug}_country',
                                'operator': 'equals',
                                'value': 'US'
                            }
                        ],
                        'logical_operator': 'AND',
                        'actions': [
                            {
                                'type': 'set_options',
                                'options': {
                                    'en': [
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
                                        {'value': 'WY', 'label': 'Wyoming'}
                                    ]
                                }
                            },
                            {'type': 'show'},
                            {'type': 'require'}
                        ]
                    },
                    {
                        'id': 'ca_provinces',
                        'conditions': [
                            {
                                'question_slug': f'{address_q.slug}_country',
                                'operator': 'equals',
                                'value': 'CA'
                            }
                        ],
                        'logical_operator': 'AND',
                        'actions': [
                            {
                                'type': 'set_options',
                                'options': {
                                    'en': [
                                        {'value': 'AB', 'label': 'Alberta'},
                                        {'value': 'BC', 'label': 'British Columbia'},
                                        {'value': 'MB', 'label': 'Manitoba'},
                                        {'value': 'NB', 'label': 'New Brunswick'},
                                        {'value': 'NL', 'label': 'Newfoundland and Labrador'},
                                        {'value': 'NS', 'label': 'Nova Scotia'},
                                        {'value': 'NT', 'label': 'Northwest Territories'},
                                        {'value': 'NU', 'label': 'Nunavut'},
                                        {'value': 'ON', 'label': 'Ontario'},
                                        {'value': 'PE', 'label': 'Prince Edward Island'},
                                        {'value': 'QC', 'label': 'Quebec'},
                                        {'value': 'SK', 'label': 'Saskatchewan'},
                                        {'value': 'YT', 'label': 'Yukon'}
                                    ]
                                }
                            },
                            {'type': 'show'},
                            {'type': 'require'}
                        ]
                    },
                    {
                        'id': 'hide_for_mexico',
                        'conditions': [
                            {
                                'question_slug': f'{address_q.slug}_country',
                                'operator': 'equals',
                                'value': 'MX'
                            }
                        ],
                        'logical_operator': 'AND',
                        'actions': [
                            {'type': 'hide'},
                            {'type': 'clear_value'},
                            {'type': 'unrequire'}
                        ]
                    }
                ],
                'default_action': 'hide'
            }
        )
        
        # Create postal code question
        Question.objects.create(
            question_group=group,
            type=text_type,
            name='Postal Code',
            slug=f'{address_q.slug}_postal',
            text='Postal Code',
            order=5,
            required=address_q.required,
            config={'placeholder': 'Postal code'},
            conditional_logic={
                'rules': [
                    {
                        'id': 'us_zip',
                        'conditions': [
                            {
                                'question_slug': f'{address_q.slug}_country',
                                'operator': 'equals',
                                'value': 'US'
                            }
                        ],
                        'logical_operator': 'AND',
                        'actions': [
                            {
                                'type': 'set_validation',
                                'validation': {
                                    'pattern': r'^\d{5}(-\d{4})?$',
                                    'custom_error_message': 'Please enter a valid ZIP code (e.g., 12345 or 12345-6789)'
                                }
                            },
                            {
                                'type': 'set_placeholder',
                                'value': '12345 or 12345-6789'
                            }
                        ]
                    },
                    {
                        'id': 'ca_postal',
                        'conditions': [
                            {
                                'question_slug': f'{address_q.slug}_country',
                                'operator': 'equals',
                                'value': 'CA'
                            }
                        ],
                        'logical_operator': 'AND',
                        'actions': [
                            {
                                'type': 'set_validation',
                                'validation': {
                                    'pattern': r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$',
                                    'custom_error_message': 'Please enter a valid Canadian postal code (e.g., K1A 0B1)'
                                }
                            },
                            {
                                'type': 'set_placeholder',
                                'value': 'K1A 0B1'
                            }
                        ]
                    }
                ]
            }
        )
        
        # Delete the original address question
        address_q.delete()
        
        self.stdout.write(f'  ✓ Converted "{address_q.name}" to question group')