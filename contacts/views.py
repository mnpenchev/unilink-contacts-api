from rest_framework import viewsets
from contacts.models import Contact, PhoneNumber
from contacts.serializers import ContactSerializer, PhoneNumberSerializer
from contacts.filters import ContactFilter
from django_filters.rest_framework import DjangoFilterBackend


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contacts and their phone numbers in one nested API.
    Key Features:
    - Nested phone numbers support for create/update.
    - Filtering support via `ContactFilter`.
    - Prefetching improves efficiency when accessing related phone numbers.
    """
    queryset = Contact.objects.all().prefetch_related("phone_numbers")
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter


class PhoneNumberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PhoneNumber directly (independent from Contact).
    Constraints:
    - `contact` must be provided in the request (POST).
    - DRF will raise 400 if (contact, type) uniqueness is violated.
    - Mainly useful for admin or direct phone number management.
    """
    queryset = PhoneNumber.objects.all().select_related("contact")
    serializer_class = PhoneNumberSerializer  # contact required here
    http_method_names = ['get', 'post']