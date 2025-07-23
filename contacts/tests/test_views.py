from rest_framework import status
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
        response = self.client.post("/api/contacts/", payload, format="json")
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
        response = self.client.post("/api/contacts/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_numbers", response.data)

    def test_list_contacts_returns_nested_phone_numbers(self):
        contact = Contact.objects.create(name="Nested", email="nested.api@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="789", type="mobile")

        response = self.client.get("/api/contacts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn("phone_numbers", response.data[0])
        self.assertEqual(response.data[0]['phone_numbers'][0]['number'], "789")

    def test_filter_contact_by_email(self):
        Contact.objects.create(name="FilterEmail", email="filter@unilink.com")
        response = self.client.get("/api/contacts/?search=filter@unilink.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_contact_by_phone_number(self):
        contact = Contact.objects.create(name="FilterPhone", email="phone@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="99999", type="mobile")
        response = self.client.get("/api/contacts/?search=99999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_name_and_phone(self):
        Contact.objects.create(name="Alice", email="a@example.com")
        contact = Contact.objects.create(name="Bob", email="b@example.com")
        PhoneNumber.objects.create(contact=contact, number="9999", type="mobile")

        response = self.client.get("/api/contacts/?name=Bob&phone=9999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Bob")

    def test_create_contact_phone_numbers_not_list_fails(self):
        payload = {
            "name": "InvalidList",
            "email": "invalidlist@unilink.com",
            "phone_numbers": {"number": "0000", "type": "mobile"}  # should be list
        }
        response = self.client.post("/api/contacts/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_numbers", response.data)

    def test_retrieve_contact_detail_includes_phone_numbers(self):
        contact = Contact.objects.create(name="Detail", email="detail@unilink.com")
        PhoneNumber.objects.create(contact=contact, number="1111", type="work")
        
        url = f"/api/contacts/{contact.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("phone_numbers", response.data)
        self.assertEqual(response.data["phone_numbers"][0]["number"], "1111")


class PhoneNumberViewSetTests(APITestCase):

    def setUp(self):
        self.contact = Contact.objects.create(name="Alice", email="alice@example.com")
        self.url = reverse("phone-number-list")

    def test_list_phone_numbers(self):
        PhoneNumber.objects.create(contact=self.contact, number="1234", type="mobile")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["number"], "1234")

    def test_create_phone_number_success(self):
        payload = {"contact": self.contact.id, "number": "5678", "type": "home"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhoneNumber.objects.count(), 1)

    def test_duplicate_type_fails(self):
        PhoneNumber.objects.create(contact=self.contact, number="1111", type="mobile")
        payload = {"contact": self.contact.id, "number": "2222", "type": "mobile"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_phone_number_without_contact_fails(self):
        payload = {"number": "5678", "type": "home"}  # no contact
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contact", response.data)

    def test_create_phone_number_invalid_type_fails(self):
        payload = {"contact": self.contact.id, "number": "9999", "type": "invalid"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)