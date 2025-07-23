from rest_framework import viewsets
from contacts.models import Contact
from contacts.serializers import ContactSerializer
from contacts.filters import ContactFilter
from django_filters.rest_framework import DjangoFilterBackend


class ContactViewSet(viewsets.ModelViewSet):
    """
    API view for managing Contact instances with nested phone numbers.
    Why ModelViewSet:
    - Provides built-in implementations for standard CRUD operations (list, create, retrieve, update, delete).
    - DRF's ModelViewSet allows us to rapidly scaffold full RESTful endpoints using less boilerplate.
    - Our use case maps exactly to CRUD (with nested serializers + filtering), so ModelViewSet is a suitable fit.
    - We add filtering via `filterset_class` (using django-filter) to extend its functionality.
    """
    queryset = Contact.objects.all().prefetch_related("phone_numbers")
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter