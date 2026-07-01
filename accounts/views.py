"""
Authentication views — register, admin_register, login, logout.

All views are function-based for clarity and simplicity.
Session management and password hashing are handled by Django's
built-in contrib.auth module.
"""

import logging

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import redirect, render

from .forms import AdopterRegistrationForm, AdminRegistrationForm, LoginForm
from .models import UserProfile

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate-limiting helper
# ---------------------------------------------------------------------------

def get_client_ip(request):
    """Extract the real client IP, checking X-Forwarded-For first."""
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def register_view(request):
    """
    Adopter registration page.
    GET  → show blank registration form.
    POST → validate, create User + profile, redirect to login with a success message.
    """
    # Redirect already-logged-in users away from the register page
    if request.user.is_authenticated:
        return redirect('pets:browse')

    if request.method == 'POST':
        form = AdopterRegistrationForm(request.POST)
        if form.is_valid():
            # Create the Django User (email doubles as the username)
            email = form.cleaned_data['email']
            user = User.objects.create_user(
                username   = email,
                email      = email,
                password   = form.cleaned_data['password1'],
                first_name = form.cleaned_data['first_name'],
                last_name  = form.cleaned_data['last_name'],
            )
            # The post_save signal in models.py creates the UserProfile automatically.
            # We just need to set the phone number if one was provided.
            if form.cleaned_data.get('phone'):
                user.profile.phone = form.cleaned_data['phone']
                user.profile.save()

            logger.info("New adopter account created: %s", email)
            messages.success(request, 'Account created! Please log in.')
            return redirect('accounts:login')
    else:
        form = AdopterRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def admin_register_view(request):
    """
    Admin registration page — protected by a secret key.
    GET  → show blank admin registration form.
    POST → validate (including secret key check), create admin User, redirect to login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.create_user(
                username   = email,
                email      = email,
                password   = form.cleaned_data['password1'],
                first_name = form.cleaned_data['first_name'],
                last_name  = form.cleaned_data['last_name'],
            )
            # Override default 'adopter' role to 'admin'
            user.profile.role = 'admin'
            if form.cleaned_data.get('phone'):
                user.profile.phone = form.cleaned_data['phone']
            user.profile.save()

            logger.info("New admin account created: %s", email)
            messages.success(request, 'Admin account created! Please log in.')
            return redirect('accounts:login')
    else:
        form = AdminRegistrationForm()

    return render(request, 'accounts/admin_register.html', {'form': form})


def login_view(request):
    """
    Login page for both Admins and Adopters.
    After a successful login, users are redirected based on their role:
      - Admin  → /dashboard/
      - Adopter → /pets/
    A 'next' query parameter overrides the default redirect.
    """
    if request.user.is_authenticated:
        return _role_redirect(request.user)

    error_message = None

    # --- Rate limiting: max 5 failed attempts per IP per 15 minutes ---
    ip = get_client_ip(request)
    cache_key = f'login_attempts_{ip}'
    attempts = cache.get(cache_key, 0)

    if attempts >= 5:
        return render(request, 'accounts/login.html', {
            'form': LoginForm(),
            'error_message': 'Too many failed attempts. Please try again in 15 minutes.',
            'rate_limited': True,
            'next': request.GET.get('next', ''),
        })

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Django uses username for authentication; our username IS the email.
            user = auth.authenticate(request, username=email, password=password)

            if user is not None:
                if not user.is_active:
                    # Account deactivated by admin — count as a failed attempt
                    cache.set(cache_key, attempts + 1, timeout=900)
                    error_message = 'Your account has been deactivated. Please contact the shelter.'
                else:
                    # Successful login — clear the failed-attempt counter
                    cache.delete(cache_key)
                    auth.login(request, user)
                    logger.info("User logged in: %s", email)

                    # Honour the 'next' param if present, otherwise redirect by role
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return _role_redirect(user)
            else:
                # Wrong credentials — increment the attempt counter
                cache.set(cache_key, attempts + 1, timeout=900)
                # Use a generic message — never reveal which field is wrong
                error_message = 'Invalid email or password. Please try again.'
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'error_message': error_message,
        'next': request.GET.get('next', ''),
    })


def logout_view(request):
    """
    Log the user out and redirect to the login page.
    We only accept POST to prevent logout via a crafted GET link (CSRF protection).
    """
    if request.method == 'POST':
        auth.logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _role_redirect(user):
    """Return the appropriate redirect response based on the user's role."""
    try:
        if user.profile.role == 'admin':
            return redirect('dashboard:home')
    except AttributeError:
        pass
    return redirect('pets:browse')
