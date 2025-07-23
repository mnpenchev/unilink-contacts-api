from rest_framework import serializers
from contacts.models import Contact, PhoneNumber
from rest_framework.exceptions import ValidationError


class PhoneNumberNestedSerializer(serializers.ModelSerializer):
    """
    Used only within ContactSerializer for nested read/write.
    `contact` is inferred from context and not required in request payload.
    """
    class Meta:
        model = PhoneNumber
        fields = ('id', 'contact', 'number', 'type')
        read_only_fields = ('contact',)  # injected from Contact serializer during save


class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    Used in standalone /api/phone-numbers/ endpoint.
    Requires `contact` to be provided explicitly.
    """
    class Meta:
        model = PhoneNumber
        fields = ('id', 'contact', 'number', 'type')  # contact required here


class ContactSerializer(serializers.ModelSerializer):
    """
    Handles full serialization and deserialization of Contact and nested phone numbers.
    Notes:
    - Allows nested creation/update of phone numbers.
    - Prevents duplicate types using `validate_phone_numbers`.
    - `contact` field on nested PhoneNumber is injected explicitly during save.
    """
    phone_numbers = PhoneNumberNestedSerializer(many=True)

    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'created_at', 'phone_numbers')
        read_only_fields = ('created_at',)

    def validate_phone_numbers(self, value):
        # Each phone type (mobile, work, home) appears only once per contact
        types = [phone['type'] for phone in value]
        if len(types) != len(set(types)):
            raise ValidationError("Duplicate phone number types are not allowed.")
        return value

    def create(self, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', [])
        contact = Contact.objects.create(**validated_data)
        # Reinject `contact` into each phone entry
        for phone_data in phone_numbers_data:
            PhoneNumber.objects.create(contact=contact, **phone_data)
        return contact

    def update(self, instance, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', None)
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if phone_numbers_data is not None:
            # Replace all existing phone numbers with new set
            instance.phone_numbers.all().delete()
            for phone_data in phone_numbers_data:
                PhoneNumber.objects.create(contact=instance, **phone_data)

        return instance