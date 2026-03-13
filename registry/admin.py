from django.contrib import admin
from .models import Donor, Recipient, OrganMatch


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_type', 'organs', 'status', 'registered_at')
    list_filter = ('blood_type', 'status')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_type', 'organ_needed', 'urgency', 'status', 'registered_at')
    list_filter = ('blood_type', 'organ_needed', 'urgency', 'status')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(OrganMatch)
class OrganMatchAdmin(admin.ModelAdmin):
    list_display = ('organ', 'donor', 'recipient', 'status', 'matched_at')
    list_filter = ('organ', 'status')
    search_fields = ('donor__first_name', 'recipient__first_name')
