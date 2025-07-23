
"""
Filtering logic for the Contact API.

This module defines filters used by the ContactViewSet to support querying contacts
by both name and related phone number.

Why this exists:
- We need to allow users to filter contacts by their `name` (a direct field)
  and by `phone number` (a related field on the PhoneNumber model).
- Using a custom `filter_by_phone` method enables filtering on the related
  `phone_numbers__number` field, which isn't natively supported by default filters.
- We use `icontains` for partial and case-insensitive search.

Example usage:
  /api/test-contacts/?name=John&phone=1234
"""
from django_filters import rest_framework as filters
from contacts.models import Contact


class ContactFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    phone = filters.CharFilter(method="filter_by_phone")

    class Meta:
        model = Contact
        fields = ["name", "phone"]

    def filter_by_phone(self, queryset, name, value):
        return queryset.filter(phone_numbers__number__icontains=value)