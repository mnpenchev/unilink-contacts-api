from rest_framework.routers import DefaultRouter
from contacts.views import ContactViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'test-contacts', ContactViewSet, basename='test-contacts')

urlpatterns = [
    path('api/', include(router.urls)),
]