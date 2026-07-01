from django.contrib import admin
from .models import Pet, PetPhoto


class PetPhotoInline(admin.TabularInline):
    """Lets admins upload photos directly from the Pet edit page."""
    model  = PetPhoto
    extra  = 1
    fields = ['image', 'caption', 'is_primary']


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display  = ['name', 'species', 'breed', 'age_display', 'location', 'status', 'listed_at']
    list_filter   = ['species', 'gender', 'size', 'status']
    search_fields = ['name', 'breed', 'location']
    inlines       = [PetPhotoInline]
