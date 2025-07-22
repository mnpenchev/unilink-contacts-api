from django.contrib import admin
from django.utils.html import format_html
from .models import Contact, PhoneNumber


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1
    verbose_name_plural = "Phone Numbers"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email_link", "phone_count", "created_at")
    search_fields = ("name", "email")
    ordering = ("-created_at",)
    inlines = [PhoneNumberInline]

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
    email_link.short_description = "Email"
    email_link.admin_order_field = "email"

    def phone_count(self, obj):
        return obj.phone_numbers.count()
    phone_count.short_description = "Phone Numbers"