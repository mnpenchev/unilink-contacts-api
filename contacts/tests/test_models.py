from django.test import TestCase
from contacts.models import TestContact, PhoneNumber


class TestContactModel(TestCase):
    def test_create_contact(self):
        contact = TestContact.objects.create(name="John", email="John@unilink.com")
        self.assertIsNotNone(contact.id)


class TestPhoneNumber(TestCase):
    def test_create_phone_number(self):
        contact = TestContact.objects.create(name="John", email="john@example.com")
        phone = PhoneNumber.objects.create(contact=contact, number="11111", type="mobile")
        self.assertEqual(phone.contact, contact)