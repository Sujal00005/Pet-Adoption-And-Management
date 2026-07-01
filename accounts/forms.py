from django import forms
from django.contrib.auth.models import User


class AdopterRegistrationForm(forms.Form):
    """
    Registration form for new Adopter accounts.
    We use a plain Form (not ModelForm) so we have full control
    over validation messages and the password confirmation logic.
    """
    first_name = forms.CharField(max_length=150, label='First Name')
    last_name  = forms.CharField(max_length=150, label='Last Name')
    email      = forms.EmailField(label='Email Address')
    phone      = forms.CharField(max_length=20, label='Phone Number',
                                  required=False)
    password1  = forms.CharField(
        widget=forms.PasswordInput,
        label='Password',
        min_length=8,
        help_text='At least 8 characters.',
    )
    password2  = forms.CharField(
        widget=forms.PasswordInput,
        label='Confirm Password',
    )

    def clean_email(self):
        """Reject registration if the email is already in use."""
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(
                'An account with this email address already exists.'
            )
        return email

    def clean_password1(self):
        """Enforce an 8-character minimum (also enforced by min_length, but explicit is clearer)."""
        password = self.cleaned_data.get('password1', '')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password

    def clean(self):
        """Make sure both password fields match."""
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'The two passwords do not match.')
        return cleaned


class LoginForm(forms.Form):
    """Simple email + password login form."""
    email    = forms.EmailField(label='Email Address')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class AdminRegistrationForm(forms.Form):
    """
    Registration form for new Admin accounts.
    Identical fields to AdopterRegistrationForm; a secret key field
    prevents random users from creating admin accounts.
    """
    first_name  = forms.CharField(max_length=150, label='First Name')
    last_name   = forms.CharField(max_length=150, label='Last Name')
    email       = forms.EmailField(label='Email Address')
    phone       = forms.CharField(max_length=20, label='Phone Number', required=False)
    password1   = forms.CharField(widget=forms.PasswordInput, label='Password', min_length=8)
    password2   = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    secret_key  = forms.CharField(
        widget=forms.PasswordInput,
        label='Admin Secret Key',
        help_text='Contact the system administrator for the admin registration key.',
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password

    def clean_secret_key(self):
        from django.conf import settings
        key = self.cleaned_data.get('secret_key', '')
        # The expected key is stored in settings.ADMIN_REGISTRATION_KEY
        expected = getattr(settings, 'ADMIN_REGISTRATION_KEY', 'changeme-admin-key')
        if key != expected:
            raise forms.ValidationError('Invalid admin secret key.')
        return key

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'The two passwords do not match.')
        return cleaned
