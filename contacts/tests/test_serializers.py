from django.test import TestCase
from contacts.models import Contact, PhoneNumber
from contacts.serializers import ContactSerializer
from rest_framework.exceptions import ValidationError


class ContactSerializerTests(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(name="John", email="john1@unilink.com")
        PhoneNumber.objects.create(contact=self.contact, number="1111", type="mobile")
        PhoneNumber.objects.create(contact=self.contact, number="2222", type="work")

    def test_serializing_contact_includes_phone_numbers(self):
        serializer = ContactSerializer(self.contact)
        data = serializer.data
        self.assertEqual(data['name'], "John")
        self.assertEqual(len(data['phone_numbers']), 2)
        self.assertEqual(data['phone_numbers'][0]['number'], "1111")

    def test_create_contact_with_nested_phone_numbers(self):
        payload = {
            "name": "Alice",
            "email": "alice1@unilink.com",
            "phone_numbers": [
                {"number": "3333", "type": "mobile"},
                {"number": "4444", "type": "home"},
            ]
        }
        serializer = ContactSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        contact = serializer.save()
        self.assertEqual(contact.phone_numbers.count(), 2)

    def test_create_contact_duplicate_phone_types_fails(self):
        payload = {
            "name": "Bob",
            "email": "bob1@unilink.com",
            "phone_numbers": [
                {"number": "5555", "type": "mobile"},
                {"number": "6666", "type": "mobile"},
            ]
        }
        serializer = ContactSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_numbers", serializer.errors)

    def test_update_contact_replaces_phone_numbers(self):
        contact = Contact.objects.create(name="Carol", email="carol1@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="1111", type="home")

        payload = {
            "name": "Carol Updated",
            "email": "carol1@unilink.com",
            "phone_numbers": [
                {"number": "2222", "type": "mobile"}
            ]
        }
        serializer = ContactSerializer(contact, data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()

        self.assertEqual(updated.name, "Carol Updated")
        self.assertEqual(updated.phone_numbers.count(), 1)
        self.assertEqual(updated.phone_numbers.first().type, "mobile")

    def test_create_contact_without_phone_numbers(self):
        payload = {
            "name": "Eve",
            "email": "eve1@unilink.com",
            "phone_numbers": []
        }
        serializer = ContactSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        contact = serializer.save()
        self.assertEqual(contact.phone_numbers.count(), 0)

    def test_create_contact_with_invalid_phone_type_fails(self):
        payload = {
            "name": "Frank",
            "email": "frank1@unilink.com",
            "phone_numbers": [
                {"number": "9999", "type": "invalid_type"}
            ]
        }
        serializer = ContactSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_numbers', serializer.errors)

    def test_create_contact_duplicate_email_fails_serializer(self):
        Contact.objects.create(name="Dupe", email="duplicate@unilink.com")
        payload = {
            "name": "New",
            "email": "duplicate@unilink.com",  # duplicate
            "phone_numbers": []
        }
        serializer = ContactSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_create_contact_with_non_list_phone_numbers_fails(self):
        payload = {
            "name": "Bad",
            "email": "bad1@unilink.com",
            "phone_numbers": {"number": "0000", "type": "mobile"}  # should be list
        }
        serializer = ContactSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_numbers", serializer.errors)

    def test_create_contact_phone_number_missing_type_fails(self):
        payload = {
            "name": "Test",
            "email": "test_missing_type@unilink.com",
            "phone_numbers": [{"number": "12345"}]  # no 'type'
        }
        serializer = ContactSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_numbers", serializer.errors)

    def test_partial_update_contact_phone_numbers_unchanged(self):
        contact = Contact.objects.create(name="Partial", email="partial@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="7777", type="mobile")
        
        payload = {"name": "Partial Updated"}
        serializer = ContactSerializer(contact, data=payload, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.phone_numbers.count(), 1)