from django.contrib import admin
from .models import SurrenderRequest


@admin.register(SurrenderRequest)
class SurrenderRequestAdmin(admin.ModelAdmin):
    list_display    = ['pet_name', 'submitter_name', 'species', 'status', 'submitted_at']
    list_filter     = ['status', 'species']
    search_fields   = ['pet_name', 'submitter_name', 'submitter_email']
    readonly_fields = ['submitted_at']
