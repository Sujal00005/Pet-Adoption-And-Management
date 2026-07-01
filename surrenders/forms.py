from django import forms


class SurrenderRequestForm(forms.Form):
    submitter_name  = forms.CharField(max_length=200, label='Your Full Name')
    submitter_phone = forms.CharField(max_length=20, label='Phone Number')
    submitter_email = forms.EmailField(label='Email Address')
    pet_name        = forms.CharField(max_length=100, label="Pet's Name")
    species         = forms.ChoiceField(choices=[
        ('', '— Select species —'),
        ('dog', 'Dog'), ('cat', 'Cat'), ('rabbit', 'Rabbit'),
        ('bird', 'Bird'), ('other', 'Other'),
    ], label='Species')
    breed           = forms.CharField(max_length=100, required=False, label='Breed (optional)')
    approximate_age = forms.CharField(max_length=50, required=False, label='Approximate Age (optional)')
    gender          = forms.ChoiceField(choices=[
        ('', '— Select —'), ('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown'),
    ], label='Gender')
    reason          = forms.CharField(widget=forms.Textarea, label='Reason for Surrender')
    is_vaccinated   = forms.BooleanField(required=False, label='Pet is vaccinated')
    health_notes    = forms.CharField(widget=forms.Textarea, required=False,
                                       label='Health Notes (optional)')

    def clean_species(self):
        val = self.cleaned_data.get('species', '')
        if not val:
            raise forms.ValidationError('Please select a species.')
        return val
