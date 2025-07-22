from django.db import models
from django.db.models import CASCADE


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)


class PhoneNumber(models.Model):
    PHONE_TYPES = (
        ('mobile', 'Mobile'),
        ('work', 'Work'),
        ('home', 'Home')
        )
    contact = models.ForeignKey(Contact, related_name='phone_numbers', on_delete=CASCADE)
    number = models.CharField(max_length=20)
    type = models.CharField(max_length=10, choices=PHONE_TYPES)

    class Meta:
        unique_together = ('contact', 'type')
        verbose_name = "Phone Number"
        verbose_name_plural = "Phone Numbers"

    def __str__(self):
        return f"{self.contact.name} - {self.type}: {self.number}"