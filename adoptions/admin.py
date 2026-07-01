from django.contrib import admin
from .models import AdoptionApplication


@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    list_display    = ['full_name', 'pet', 'status', 'submitted_at', 'reviewed_at']
    list_filter     = ['status']
    search_fields   = ['full_name', 'pet__name', 'applicant__email']
    readonly_fields = ['submitted_at']
