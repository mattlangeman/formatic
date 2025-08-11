import factory
from factory.django import DjangoModelFactory
from apps.form_builder.factories import (
    DynamicFormFactory, FormVersionFactory, FormSubmissionFactory,
    PublishedFormVersionFactory
)


class APIFormFactory(DynamicFormFactory):
    """Factory for API-specific form testing scenarios"""
    is_active = True


class APIPublishedFormVersionFactory(PublishedFormVersionFactory):
    """Factory for API testing with published versions"""
    form = factory.SubFactory(APIFormFactory)


class APIFormSubmissionFactory(FormSubmissionFactory):
    """Factory for API submission testing"""
    form_version = factory.SubFactory(APIPublishedFormVersionFactory)
    ip_address = factory.Faker('ipv4')