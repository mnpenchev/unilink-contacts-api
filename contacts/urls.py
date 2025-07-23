from rest_framework.routers import DefaultRouter
from contacts.views import ContactViewSet, PhoneNumberViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contacts')
router.register("phone-numbers", PhoneNumberViewSet, basename="phone-number")

urlpatterns = [
    path('api/', include(router.urls)),
]