"""
Forms for the pets app.

PetFilterForm      — GET-based filter form used on the public browsing page.
PetPhotoForm       — Upload form used by admins to add a photo to a pet listing.

BREEDS_BY_SPECIES is a dict keyed by species that the browsing page's JS
uses to populate the breed dropdown dynamically when species changes.
"""

import os

from django import forms

from .models import Pet


# ---------------------------------------------------------------------------
# Breed lookup — grouped by species.
# Intentionally separate from the model so the view can serialise it to JSON
# and pass it straight into the page's inline <script>.
# ---------------------------------------------------------------------------

BREEDS_BY_SPECIES = {
    'dog': [
        'Labrador', 'German Shepherd', 'Golden Retriever', 'Beagle',
        'Poodle', 'Bulldog', 'Rottweiler', 'Dachshund', 'Shih Tzu',
        'Mixed Breed',
    ],
    'cat': [
        'Persian', 'Siamese', 'Maine Coon', 'British Shorthair', 'Ragdoll',
        'Bengal', 'Sphynx', 'Abyssinian', 'Mixed Breed',
    ],
    'rabbit': [
        'Holland Lop', 'Lionhead', 'Dutch', 'Rex', 'Mini Rex', 'Mixed Breed',
    ],
    'bird': [
        'Budgerigar', 'Cockatiel', 'Lovebird', 'Parrot', 'Canary', 'Finch',
    ],
    'other': [
        'Mixed Breed', 'Unknown',
    ],
}


# ---------------------------------------------------------------------------
# Public filter form — submitted via GET so filters appear in the URL
# ---------------------------------------------------------------------------

class PetFilterForm(forms.Form):
    """
    Unbound, GET-based filter form for the pet browsing page.
    All fields are optional — leaving them blank shows all available pets.
    """

    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by name, breed…'}),
    )
    species = forms.ChoiceField(
        required=False,
        label='Species',
        choices=[('', 'All Species')] + Pet.SPECIES_CHOICES,
    )
    breed = forms.CharField(
        required=False,
        label='Breed',
        widget=forms.TextInput(attrs={'placeholder': 'Any breed'}),
    )
    gender = forms.ChoiceField(
        required=False,
        label='Gender',
        choices=[('', 'Any Gender')] + Pet.GENDER_CHOICES,
    )
    size = forms.ChoiceField(
        required=False,
        label='Size',
        choices=[('', 'Any Size')] + Pet.SIZE_CHOICES,
    )
    location = forms.CharField(
        required=False,
        label='City',
        widget=forms.TextInput(attrs={'placeholder': 'Any city'}),
    )
    min_age_years = forms.IntegerField(
        required=False,
        min_value=0,
        label='Min Age (yrs)',
        widget=forms.NumberInput(attrs={'placeholder': '0'}),
    )
    max_age_years = forms.IntegerField(
        required=False,
        min_value=0,
        label='Max Age (yrs)',
        widget=forms.NumberInput(attrs={'placeholder': '20'}),
    )


# ---------------------------------------------------------------------------
# Admin photo upload form
# ---------------------------------------------------------------------------

class PetPhotoForm(forms.Form):
    """Form for uploading a single pet photo (used by admins only)."""

    image = forms.ImageField(label='Photo', required=False)
    caption = forms.CharField(
        max_length=200,
        required=False,
        label='Caption',
    )
    is_primary = forms.BooleanField(
        required=False,
        label='Set as primary photo',
    )

    def clean_image(self):
        """Validate file size (≤ 5 MB) and file type (JPEG, PNG, WebP)."""
        image = self.cleaned_data.get('image')
        if image:
            # Enforce 5 MB file size limit
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image must be 5 MB or smaller.')

            # Check MIME type when available
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise forms.ValidationError(
                    'Only JPEG, PNG, and WebP images are accepted.'
                )

            # Fallback: check file extension
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise forms.ValidationError(
                    'Only .jpg, .jpeg, .png, and .webp files are accepted.'
                )
        return image
