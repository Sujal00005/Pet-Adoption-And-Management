"""
Forms for the adoptions app.
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import AdoptionApplication


class AdoptionApplicationForm(forms.ModelForm):
    """
    Adoption application form filled out by an authenticated adopter.

    Personal details are pre-filled from the user's profile on GET.
    Validation enforces landlord contact when renting and requires agreement
    to a home visit before submission.
    """

    class Meta:
        model = AdoptionApplication
        fields = [
            'full_name',
            'phone',
            'address',
            'housing_type',
            'owns_or_rents',
            'landlord_contact',
            'household_members',
            'has_other_pets',
            'other_pets_desc',
            'prev_pet_experience',
            'reason_for_adoption',
            'agrees_to_home_visit',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'prev_pet_experience': forms.Textarea(attrs={'rows': 3}),
            'reason_for_adoption': forms.Textarea(attrs={'rows': 4, 'maxlength': 1000}),
            'other_pets_desc': forms.TextInput(attrs={'placeholder': 'e.g. 1 cat, 2 fish'}),
            'landlord_contact': forms.TextInput(attrs={'placeholder': 'Landlord name and phone'}),
            'household_members': forms.NumberInput(attrs={'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        owns_or_rents = cleaned_data.get('owns_or_rents')
        landlord_contact = cleaned_data.get('landlord_contact', '').strip()
        agrees = cleaned_data.get('agrees_to_home_visit')

        if owns_or_rents == 'rents' and not landlord_contact:
            self.add_error(
                'landlord_contact',
                'Landlord contact is required when you rent your home.',
            )

        if not agrees:
            self.add_error(
                'agrees_to_home_visit',
                'You must agree to a home visit to submit an application.',
            )

        return cleaned_data
