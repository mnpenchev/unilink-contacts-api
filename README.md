# Unilink Contacts API

This is a Django REST Framework (DRF) project that manages contacts and their associated phone numbers. 
It supports full CRUD functionality, nested serialization, validation, and filtering.

## Setup Instructions

### 1. Clone the repository:
git clone https://github.com/mnpenchev/unilink-contacts-api.git
cd unilink-contacts-api
To open directly in Gitpod:
https://gitpod.io/#https://github.com/mnpenchev/unilink-contacts-api
### 2. Install dependencies:
pip install -r requirements.txt
### 3. Run the server:
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

Then open the browser to:
http://localhost:8000/api/contacts/
### 4. Run tests:
python manage.py test

## API Endpoints

### /api/contacts/

- GET: List all contacts, including their phone numbers
- POST: Create a new contact with optional nested phone numbers
- Supports filtering by email and phone number via query params:
  - `?email=example@example.com`
  - `?phone=1234567890`

### /api/contacts/<id>/

- GET: Retrieve a single contact with phone numbers
- PUT: Update a contact and replace phone numbers
- DELETE: Delete a contact and all its phone numbers

### /api/phone-numbers/

- GET: List all phone numbers
- POST: Create a phone number (requires a `contact` ID)

## Design Decisions

- Contacts and phone numbers are modeled as separate entities with a foreign key relationship.
- Each contact can have at most one phone number of each type (mobile, work, home). This is enforced both at the serializer level and database level using a unique constraint.
- Two serializers are used for `PhoneNumber`:
  - One for nested use inside the `ContactSerializer`, where `contact` is injected automatically.
  - One standalone for the `/api/phone-numbers/` endpoint, where `contact` is required.
- DRF’s `ModelViewSet` is used to reduce boilerplate and make the code easier to extend.
- Filtering is implemented using `django-filter` to allow searching by phone number or email.

## Notes

- The Contact model is named `Contact` for clarity even though the spec refers to `TestContact`.
- Routes use `/api/contacts/` as per REST naming conventions.
- Gitpod users may need to manually expose port 8000 in the workspace UI.

## Repository

https://github.com/mnpenchev/unilink-contacts-api