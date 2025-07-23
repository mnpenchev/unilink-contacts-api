from rest_framework.test import APITestCase
from contacts.models import Contact, PhoneNumber


class ContactIntegrationTests(APITestCase):
    def test_create_and_retrieve_contact_with_nested_phone_numbers(self):
        payload = {
            "name": "Test User",
            "email": "testuser@example.com",
            "phone_numbers": [
                {"number": "1111", "type": "mobile"},
                {"number": "2222", "type": "home"},
            ]
        }
        # Create contact
        response = self.client.post("/api/contacts/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Test User")
        self.assertEqual(len(response.data["phone_numbers"]), 2)

        # Retrieve contact
        contact_id = response.data["id"]
        get_response = self.client.get(f"/api/contacts/{contact_id}/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data["email"], "testuser@example.com")
        self.assertEqual(len(get_response.data["phone_numbers"]), 2)

    def test_update_contact_replaces_phone_numbers(self):
        contact = Contact.objects.create(name="ToUpdate", email="update@example.com")
        PhoneNumber.objects.create(contact=contact, number="1234", type="home")

        payload = {
            "name": "Updated Name",
            "email": "update@example.com",
            "phone_numbers": [
                {"number": "5678", "type": "mobile"},
            ]
        }
        response = self.client.put(f"/api/contacts/{contact.id}/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Name")

        contact.refresh_from_db()
        self.assertEqual(contact.phone_numbers.count(), 1)
        self.assertEqual(contact.phone_numbers.first().type, "mobile")

    def test_duplicate_phone_number_type_fails(self):
        payload = {
            "name": "DupTest",
            "email": "duptest@example.com",
            "phone_numbers": [
                {"number": "0001", "type": "work"},
                {"number": "0002", "type": "work"},
            ]
        }
        response = self.client.post("/api/contacts/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_numbers", response.data)

    def test_filter_by_email(self):
        Contact.objects.create(name="EmailFilter", email="findme@example.com")
        response = self.client.get("/api/contacts/?search=findme@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "findme@example.com")

    def test_filter_by_phone_number(self):
        contact = Contact.objects.create(name="PhoneFilter", email="pf@example.com")
        PhoneNumber.objects.create(contact=contact, number="7890", type="mobile")

        response = self.client.get("/api/contacts/?search=7890")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "PhoneFilter")
