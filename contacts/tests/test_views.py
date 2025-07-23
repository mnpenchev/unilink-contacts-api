from rest_framework.test import APITestCase
from contacts.models import Contact, PhoneNumber
from django.urls import reverse


class TestContactAPI(APITestCase):
    def test_create_contact_with_phone_numbers(self):
        payload = {
            "name": "John",
            "email": "john.api@unilink.com",
            "phone_numbers": [
                {"number": "123", "type": "mobile"},
                {"number": "456", "type": "work"}
            ]
        }
        response = self.client.post("/api/test-contacts/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['phone_numbers']), 2)

    def test_create_contact_duplicate_phone_type_fails(self):
        payload = {
            "name": "FailCase",
            "email": "fail.api@unilink.com",
            "phone_numbers": [
                {"number": "123", "type": "home"},
                {"number": "456", "type": "home"}
            ]
        }
        response = self.client.post("/api/test-contacts/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_numbers", response.data)

    def test_list_contacts_returns_nested_phone_numbers(self):
        contact = Contact.objects.create(name="Nested", email="nested.api@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="789", type="mobile")

        response = self.client.get("/api/test-contacts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn("phone_numbers", response.data[0])
        self.assertEqual(response.data[0]['phone_numbers'][0]['number'], "789")

    def test_filter_contact_by_email(self):
        Contact.objects.create(name="FilterEmail", email="filter@unilink.com")
        response = self.client.get("/api/test-contacts/?search=filter@unilink.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_contact_by_phone_number(self):
        contact = Contact.objects.create(name="FilterPhone", email="phone@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="99999", type="mobile")
        response = self.client.get("/api/test-contacts/?search=99999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_name_and_phone(self):
        Contact.objects.create(name="Alice", email="a@example.com")
        contact = Contact.objects.create(name="Bob", email="b@example.com")
        PhoneNumber.objects.create(contact=contact, number="9999", type="mobile")

        response = self.client.get("/api/test-contacts/?name=Bob&phone=9999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Bob")