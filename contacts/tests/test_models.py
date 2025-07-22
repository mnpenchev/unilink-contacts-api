from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from contacts.models import Contact, PhoneNumber


class TestContactModel(TestCase):
    def test_create_contact(self):
        contact = Contact.objects.create(name="John", email="john@unilink.com")
        self.assertIsNotNone(contact.id)

    def test_duplicate_email_fails(self):
        Contact.objects.create(name="John", email="john@unilink.com")
        with self.assertRaises(IntegrityError):
            Contact.objects.create(name="Jane", email="john@unilink.com")

    def test_blank_email_fails(self):
        contact = Contact(name="John", email="")
        with self.assertRaises(Exception):
            contact.full_clean()
            contact.save()

    def test_contact_deletion_removes_phone_numbers(self):
        contact = Contact.objects.create(name="John", email="john@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="12345", type="mobile")
        contact.delete()
        self.assertEqual(PhoneNumber.objects.count(), 0)


class TestPhoneNumber(TestCase):
    def test_create_phone_number(self):
        contact = Contact.objects.create(name="John", email="john@unilink.com")
        phone = PhoneNumber.objects.create(contact=contact, number="11111", type="mobile")
        self.assertEqual(phone.contact, contact)

    def test_cannot_create_duplicate_phone_type(self):
        contact = Contact.objects.create(name="John", email="john@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="12345", type="mobile")

        with self.assertRaises(IntegrityError):
            PhoneNumber.objects.create(contact=contact, number="67890", type="mobile")

    def test_can_create_same_type_on_different_contacts(self):
        contact1 = Contact.objects.create(name="John", email="john@unilink.com")
        contact2 = Contact.objects.create(name="Alice", email="alice@unilink.com")

        PhoneNumber.objects.create(contact=contact1, number="12345", type="mobile")
        try:
            PhoneNumber.objects.create(contact=contact2, number="67890", type="mobile")
        except IntegrityError:
            self.fail("Should allow same phone type on different contacts")

    def test_phone_number_str_representation(self):
        contact = Contact.objects.create(name="Bob", email="bob@unilink.com")
        phone = PhoneNumber.objects.create(contact=contact, number="88888", type="work")
        self.assertEqual(str(phone), "Bob - work: 88888")

    def test_invalid_type_raises_exception(self):
        contact = Contact.objects.create(name="John", email="john@unilink.com")
        phone = PhoneNumber(contact=contact, number="99999", type="personal")  # invalid choice
        with self.assertRaises(ValidationError):
            phone.full_clean()

    def test_missing_number_fails(self):
        contact = Contact.objects.create(name="John", email="john@unilink.com")
        phone = PhoneNumber(contact=contact, type="home")  # missing number
        with self.assertRaises(Exception):
            phone.full_clean()
            phone.save()