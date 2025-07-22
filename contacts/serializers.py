from rest_framework import serializers
from contacts.models import Contact, PhoneNumber
from rest_framework.exceptions import ValidationError


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ('id', 'number', 'type')


class ContactSerializer(serializers.ModelSerializer):
    phone_numbers = PhoneNumberSerializer(many=True)

    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'created_at', 'phone_numbers')
        read_only_fields = ('created_at',)

    def validate_phone_numbers(self, value):
        types = [phone['type'] for phone in value]
        if len(types) != len(set(types)):
            raise ValidationError("Duplicate phone number types are not allowed.")
        return value

    def create(self, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', [])
        contact = Contact.objects.create(**validated_data)
        for phone_data in phone_numbers_data:
            PhoneNumber.objects.create(contact=contact, **phone_data)
        return contact

    def update(self, instance, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', None)
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if phone_numbers_data is not None:
            # delete existing phone numbers and recreate
            instance.phone_numbers.all().delete()
            for phone_data in phone_numbers_data:
                PhoneNumber.objects.create(contact=instance, **phone_data)

        return instance