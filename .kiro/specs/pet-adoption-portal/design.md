# Design Document: Pet Adoption and Rescue Management Portal

## Overview

The Pet Adoption and Rescue Management Portal is a Django-based web application that manages the complete lifecycle of pet adoption — from listing rescued animals and accepting surrender requests, through processing adoption applications and tracking outcomes.

### Core User Roles

- **Admin** — Shelter staff who manage pet listings, review applications, and administer the portal.
- **Adopter** — Registered members of the public who browse pets and submit adoption applications.
- **Public Visitor** — Unauthenticated users who can browse pets and submit surrender forms.

### Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend | HTML + CSS (custom stylesheet) + vanilla JavaScript |
| Backend | Django 4.x (Python) |
| Database | SQLite |
| Auth | Django's built-in `django.contrib.auth` |
| Email | `django.core.mail` + Gmail SMTP |
| File Storage | Django `MEDIA_ROOT` / `FileSystemStorage` |
| Templates | Django Template Language (DTL) |

> **No external CSS frameworks, no npm, no Node.js, no third-party JS libraries.** Everything is plain HTML, hand-written CSS, and vanilla JavaScript. Django's standard library covers all backend needs.

### Design Philosophy

- **Keep it simple**: Only the four technologies the developer knows — Python/Django, SQL (via Django ORM), HTML/CSS, and basic JavaScript. Nothing else.
- **Beginner-friendly**: Function-based views (FBVs) throughout — easier to read top-to-bottom than class-based views. Each view is a plain Python function.
- **Django-native**: Lean on the framework — Django auth, Django forms, Django ORM, Django sessions, CSRF protection. No third-party packages needed.
- **Clean and readable code**: Meaningful variable names, short functions with single responsibilities, comments explaining the "why" not the "what".
- **Extensible**: App boundaries are drawn so that future apps (foster, donations, volunteers) can be added without touching existing code.

---

## Architecture

### High-Level Architecture

```
Browser
  │
  ▼
Django Development Server (manage.py runserver)
  │
  ├── URL Router (urls.py)
  │       │
  │       ├── accounts/  ─── AccountsApp (registration, login, logout)
  │       ├── pets/      ─── PetsApp     (listing, browsing, profiles)
  │       ├── adoptions/ ─── AdoptionsApp (applications, status tracking)
  │       ├── surrenders/─── SurrendersApp (surrender form, admin review)
  │       └── dashboard/ ─── DashboardApp  (admin overview, user mgmt)
  │
  ├── Django ORM ──► SQLite database (db.sqlite3)
  ├── Django Auth ─► Session Middleware
  ├── Django Media ► MEDIA_ROOT (uploaded photos)
  └── django.core.mail ► Gmail SMTP
```

### Request Lifecycle

1. Browser sends HTTP request.
2. Django middleware runs: `SessionMiddleware`, `AuthenticationMiddleware`, `CsrfViewMiddleware`.
3. URL router matches the path and calls the appropriate view.
4. The view queries the database via ORM models, processes business logic, and renders a template.
5. The template is returned as an HTTP response.
6. For form submissions (`POST`), CSRF token is verified by middleware before the view runs.

### Project Directory Layout

```
pet_adoption/                  ← Django project root
├── manage.py
├── pet_adoption/              ← Project package (settings, root urls)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                  ← User registration, login, logout
│   ├── migrations/
│   ├── templates/accounts/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── pets/                      ← Pet listings and profiles
│   ├── migrations/
│   ├── templates/pets/
│   ├── templatetags/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── adoptions/                 ← Adoption applications and status tracking
│   ├── migrations/
│   ├── templates/adoptions/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── surrenders/                ← Public surrender request form
│   ├── migrations/
│   ├── templates/surrenders/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── dashboard/                 ← Admin dashboard, stats, user management
│   ├── templates/dashboard/
│   ├── urls.py
│   └── views.py
├── notifications/             ← Email notification helpers
│   ├── __init__.py
│   └── emails.py
├── templates/                 ← Shared base templates
│   ├── base.html
│   ├── navbar.html
│   └── 403.html, 404.html, 500.html
├── static/                    ← Static assets (icons, custom CSS)
├── media/                     ← Uploaded pet photos (MEDIA_ROOT)
└── requirements.txt
```

---

## Components and Interfaces

### App Responsibilities

#### `accounts` app
- Custom `UserProfile` model extending Django's `User`.
- Registration form and view for Adopters.
- Separate admin registration page (not `/admin`).
- Login/logout views using Django's `LoginView`/`LogoutView` as base.
- Role-based redirect after login (Admin → dashboard, Adopter → pets list).

#### `pets` app
- `Pet` and `PetPhoto` models.
- Public browsing page with search and filter.
- Pet profile detail page.
- Admin CRUD views for pet management (add, edit, delete, mark as adopted).

#### `adoptions` app
- `AdoptionApplication` model.
- Adopter application submission and "My Applications" page.
- Admin application review views (approve, reject, under review).
- Status update triggers email notification.

#### `surrenders` app
- `SurrenderRequest` model.
- Public surrender form (no auth required).
- Admin surrender request management section.

#### `dashboard` app
- Admin dashboard home with summary statistics.
- Recent activity feed.
- User management section.
- Aggregates data from other apps — no models of its own.

#### `notifications` package
- Thin helper module containing email-sending functions.
- Called by views in `adoptions` and `surrenders` when notifications are needed.
- Not a Django app (no models, no URLs) — just a Python package.

### View Design Patterns

All views are **function-based views (FBVs)** — plain Python functions that take a `request` and return a `response`. This is the simplest, most readable pattern and easiest to learn.

```
View type        When to use
─────────────────────────────────────────────────────────
FBV + @login_required     All pages requiring authentication
FBV + @admin_required     All admin-only pages
FBV (no decorator)        Public pages (pet browsing, surrender form, login, register)
```

### URL Routing Plan

```
/                           → Redirect: logged-in users → role home; visitors → pets list
/accounts/register/         → Adopter registration (AccountsApp)
/accounts/admin-register/   → Admin registration (AccountsApp, invite-only or secret key)
/accounts/login/            → Shared login page (AccountsApp)
/accounts/logout/           → Logout (AccountsApp)

/pets/                      → Pet browsing/search page (PetsApp)
/pets/<int:pk>/             → Pet profile detail (PetsApp)

/adoptions/apply/<int:pet_pk>/  → Adoption application form (AdoptionsApp)
/adoptions/my-applications/     → Adopter: My Applications (AdoptionsApp)
/adoptions/<int:pk>/            → Application detail view (AdoptionsApp)

/surrender/                 → Public surrender form (SurrendersApp)
/surrender/success/         → Surrender confirmation page (SurrendersApp)

/dashboard/                 → Admin dashboard home (DashboardApp)
/dashboard/pets/            → Admin: Pet management list (PetsApp, admin view)
/dashboard/pets/add/        → Admin: Add pet (PetsApp)
/dashboard/pets/<int:pk>/edit/   → Admin: Edit pet (PetsApp)
/dashboard/pets/<int:pk>/delete/ → Admin: Delete pet (PetsApp)
/dashboard/applications/         → Admin: All applications (AdoptionsApp)
/dashboard/applications/<int:pk>/review/ → Admin: Review application (AdoptionsApp)
/dashboard/users/                → Admin: User list (DashboardApp)
/dashboard/users/<int:pk>/       → Admin: User detail (DashboardApp)
/dashboard/surrenders/           → Admin: Surrender requests (SurrendersApp)
/dashboard/surrenders/<int:pk>/  → Admin: Review surrender (SurrendersApp)
```

### Template Structure

All templates extend a shared `base.html` that links to a hand-written `static/css/style.css` and defines the page skeleton.

```
base.html
  ├── blocks: title, extra_head, content, extra_scripts
  ├── links: static/css/style.css  (custom hand-written CSS)
  └── includes: navbar.html (conditional: admin nav vs adopter nav)

accounts/
  ├── register.html          (extends base.html)
  ├── admin_register.html    (extends base.html)
  └── login.html             (extends base.html)

pets/
  ├── browse.html            (extends base.html) ← filter sidebar + grid
  └── detail.html            (extends base.html) ← profile + photo gallery

adoptions/
  ├── apply.html             (extends base.html)
  ├── my_applications.html   (extends base.html)
  └── application_detail.html(extends base.html)

surrenders/
  ├── form.html              (extends base.html)
  └── success.html           (extends base.html)

dashboard/
  ├── home.html              (extends base.html) ← stats cards + activity feed
  ├── pets_list.html         (extends base.html)
  ├── pet_form.html          (extends base.html) ← shared add/edit form
  ├── applications_list.html (extends base.html)
  ├── application_review.html(extends base.html)
  ├── users_list.html        (extends base.html)
  ├── user_detail.html       (extends base.html)
  ├── surrenders_list.html   (extends base.html)
  └── surrender_detail.html  (extends base.html)
```

### Custom Decorators / Mixins

Since we use FBVs exclusively, access control is done with simple Python decorators:

```python
# accounts/decorators.py

from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_required(view_func):
    """Decorator: only allows users with role == 'admin'. Returns 403 otherwise."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('accounts:login')
        if request.user.profile.role != 'admin':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def adopter_required(view_func):
    """Decorator: only allows authenticated users (any role). Redirects to login otherwise."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

## Data Models

### `accounts` app

#### `UserProfile` model

Django's built-in `User` model handles username (we'll use email as username), password hashing, and session management. `UserProfile` extends it with role and extra contact info.

```python
class UserProfile(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('adopter', 'Adopter')]

    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default='adopter')
    phone       = models.CharField(max_length=20, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"
```

A Django signal (`post_save` on `User`) automatically creates a linked `UserProfile` when a new user is registered, keeping the creation logic in one place.

---

### `pets` app

#### `Pet` model

```python
class Pet(models.Model):
    SPECIES_CHOICES = [('dog', 'Dog'), ('cat', 'Cat'), ('rabbit', 'Rabbit'),
                       ('bird', 'Bird'), ('other', 'Other')]
    GENDER_CHOICES  = [('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')]
    SIZE_CHOICES    = [('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'),
                       ('xlarge', 'Extra Large')]
    STATUS_CHOICES  = [('available', 'Available'), ('adopted', 'Adopted'),
                       ('pending', 'Pending'), ('unavailable', 'Unavailable')]

    name              = models.CharField(max_length=100)
    species           = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed             = models.CharField(max_length=100, blank=True)
    age_years         = models.PositiveSmallIntegerField(default=0)
    age_months        = models.PositiveSmallIntegerField(default=0)
    gender            = models.CharField(max_length=10, choices=GENDER_CHOICES)
    size              = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color_markings    = models.CharField(max_length=200, blank=True)
    description       = models.TextField()
    temperament       = models.TextField(blank=True)
    good_with_kids    = models.BooleanField(default=False)
    good_with_pets    = models.BooleanField(default=False)
    # Health status
    is_vaccinated     = models.BooleanField(default=False)
    is_neutered       = models.BooleanField(default=False)
    medical_notes     = models.TextField(blank=True)
    # Location and listing
    location          = models.CharField(max_length=150)   # Free-text city name
    status            = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    listed_at         = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)
    added_by          = models.ForeignKey(User, on_delete=models.SET_NULL,
                                           null=True, related_name='added_pets')

    class Meta:
        ordering = ['-listed_at']

    def __str__(self):
        return f"{self.name} ({self.species})"

    @property
    def primary_photo(self):
        """Returns the first photo or None."""
        return self.photos.first()

    @property
    def age_display(self):
        """Human-readable age string, e.g. '2 years 3 months'."""
        parts = []
        if self.age_years:
            parts.append(f"{self.age_years} yr{'s' if self.age_years != 1 else ''}")
        if self.age_months:
            parts.append(f"{self.age_months} mo")
        return ', '.join(parts) or 'Unknown'
```

#### `PetPhoto` model

```python
def pet_photo_upload_path(instance, filename):
    """Organise uploads into per-pet subdirectories: media/pets/<pet_id>/filename"""
    return f"pets/{instance.pet.pk}/{filename}"


class PetPhoto(models.Model):
    pet        = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='photos')
    image      = models.ImageField(upload_to=pet_photo_upload_path)
    caption    = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f"Photo for {self.pet.name} ({'primary' if self.is_primary else 'gallery'})"
```

---

### `adoptions` app

#### `AdoptionApplication` model

```python
class AdoptionApplication(models.Model):
    HOUSING_CHOICES = [('house', 'House'), ('apartment', 'Apartment'), ('other', 'Other')]
    STATUS_CHOICES  = [
        ('pending',      'Pending'),
        ('under_review', 'Under Review'),
        ('approved',     'Approved'),
        ('rejected',     'Rejected'),
    ]

    # Core relationships
    pet         = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='applications')
    applicant   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')

    # Applicant details (captured at submission time — not linked live to profile)
    full_name      = models.CharField(max_length=200)
    phone          = models.CharField(max_length=20)
    address        = models.TextField()
    housing_type   = models.CharField(max_length=15, choices=HOUSING_CHOICES)
    owns_or_rents  = models.CharField(max_length=10, choices=[('owns', 'Owns'), ('rents', 'Rents')])
    landlord_contact = models.CharField(max_length=200, blank=True)

    # Household
    household_members = models.PositiveSmallIntegerField(default=1)
    has_other_pets    = models.BooleanField(default=False)
    other_pets_desc   = models.CharField(max_length=300, blank=True)
    prev_pet_experience = models.TextField(blank=True)

    # Adoption intent
    reason_for_adoption = models.TextField()
    agrees_to_home_visit = models.BooleanField(default=False)

    # Status tracking
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    admin_remarks   = models.TextField(blank=True)
    submitted_at    = models.DateTimeField(auto_now_add=True)
    reviewed_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        # One application per pet per applicant
        unique_together = [('pet', 'applicant')]

    def __str__(self):
        return f"{self.full_name} → {self.pet.name} [{self.status}]"
```

---

### `surrenders` app

#### `SurrenderRequest` model

```python
class SurrenderRequest(models.Model):
    REVIEWED_STATUS = [('new', 'New'), ('reviewed', 'Reviewed')]

    # Submitter info
    submitter_name  = models.CharField(max_length=200)
    submitter_phone = models.CharField(max_length=20)
    submitter_email = models.EmailField()

    # Pet info
    pet_name        = models.CharField(max_length=100)
    species         = models.CharField(max_length=50)
    breed           = models.CharField(max_length=100, blank=True)
    approximate_age = models.CharField(max_length=50, blank=True)
    gender          = models.CharField(max_length=10, blank=True)
    is_vaccinated   = models.BooleanField(default=False)
    health_notes    = models.TextField(blank=True)
    reason          = models.TextField()

    # Admin tracking
    status          = models.CharField(max_length=10, choices=REVIEWED_STATUS, default='new')
    admin_notes     = models.TextField(blank=True)
    submitted_at    = models.DateTimeField(auto_now_add=True)
    reviewed_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Surrender: {self.pet_name} by {self.submitter_name}"
```

### Entity-Relationship Overview

```
User (Django built-in)
 │  1──1  UserProfile (role, phone)
 │
 │  1──N  AdoptionApplication
 │  1──N  Pet (added_by)
 │
Pet
 │  1──N  PetPhoto
 │  1──N  AdoptionApplication

SurrenderRequest (standalone — no FK to User or Pet)
```

---

## Error Handling

### Form Validation Errors

Django forms handle field-level validation. Templates render `{{ form.field.errors }}` inline beside each input, styled with plain CSS (`.error-msg { color: #c0392b; font-size: 0.85rem; }`). Non-field errors are rendered in a banner at the top of the form using `{{ form.non_field_errors }}`.

### HTTP Error Pages

Custom templates in `templates/` override Django's defaults:

| Template | Trigger |
|---|---|
| `403.html` | `PermissionDenied` raised by `AdminRequiredMixin` |
| `404.html` | `Http404` or `get_object_or_404` failure |
| `500.html` | Unhandled server exceptions in production |

### File Upload Validation

Photo uploads are validated both on the Django form and in the view:

```python
# pets/forms.py
def clean_image(self):
    image = self.cleaned_data.get('image')
    if image:
        if image.size > 5 * 1024 * 1024:      # 5 MB limit
            raise ValidationError("Image must be 5 MB or smaller.")
        valid_types = ['image/jpeg', 'image/png', 'image/webp']
        if image.content_type not in valid_types:
            raise ValidationError("Only JPEG, PNG, and WebP images are accepted.")
    return image
```

### Email Send Failures

Email sending is wrapped in a `try/except` block. If the SMTP call fails, the error is logged using Django's `logging` module and the user-facing flow continues (the application is still saved — email failure is non-fatal).

```python
# notifications/emails.py
import logging
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

def send_application_confirmation(application):
    try:
        send_mail(
            subject=f"Application Received — {application.pet.name}",
            message=...,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.applicant.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send application confirmation email for application %d",
                         application.pk)
```

### Database Errors

ORM operations are wrapped in `try/except` blocks only at points where partial writes are a risk (e.g., approving an application and updating the pet status). Django's `transaction.atomic()` is used to ensure atomicity for multi-model updates.

```python
from django.db import transaction

with transaction.atomic():
    application.status = 'approved'
    application.save()
    application.pet.status = 'adopted'
    application.pet.save()
    # Reject all other applications for this pet
    AdoptionApplication.objects.filter(
        pet=application.pet,
        status__in=['pending', 'under_review']
    ).exclude(pk=application.pk).update(status='rejected')
```

---

## Testing Strategy

### Unit Tests

Located in `<app>/tests.py`. Focus on:

- **Model methods**: `Pet.age_display`, `Pet.primary_photo`, `UserProfile.__str__`
- **Form validation**: empty required fields, invalid email, image size over limit, duplicate application
- **View access control**: unauthenticated access returns redirect; adopter accessing admin route returns 403

Example test structure:

```python
# pets/tests.py
from django.test import TestCase
from pets.models import Pet

class PetAgeDisplayTest(TestCase):
    def test_years_and_months(self):
        pet = Pet(age_years=2, age_months=3)
        self.assertEqual(pet.age_display, "2 yrs, 3 mo")

    def test_only_years(self):
        pet = Pet(age_years=1, age_months=0)
        self.assertEqual(pet.age_display, "1 yr")

    def test_unknown_age(self):
        pet = Pet(age_years=0, age_months=0)
        self.assertEqual(pet.age_display, "Unknown")
```

### Integration Tests

Django's `TestCase` with `self.client` for testing full request-response cycles:

- Registration flow: POST valid data → account created → redirect to login
- Login flow: valid credentials → session created → redirect to correct home
- Application submission: POST form → application record created → email sent (using `mail.outbox`)
- Application approval: POST approve → application `Approved`, pet `Adopted`, other applications `Rejected`

### Property-Based Tests

See **Correctness Properties** section below. Implemented using Django's built-in `TestCase` with parameterized data (no external PBT library needed), with multiple data variations per property covering edge cases.

Each property test is clearly commented:
```python
# Property N: <property description>
def test_property_N_name(self):
    ...
```

### Manual Testing Checklist

- Mobile responsiveness across 320px, 768px, 1024px, 1440px viewports
- Screen reader navigation through key pages
- Keyboard-only navigation through all forms

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Valid registration always creates an Adopter account

*For any* combination of a unique email address, a valid full name, a phone number, and a password of at least 8 characters, submitting the registration form SHALL create exactly one new user account with `role = 'adopter'`, increasing the total user count by exactly one.

**Validates: Requirements 1.2**

---

### Property 2: Duplicate email registration is always rejected

*For any* email address that is already registered in the system, a second registration attempt using that same email SHALL be rejected — no new user account is created and the user count remains unchanged.

**Validates: Requirements 1.3**

---

### Property 3: Short passwords are always rejected

*For any* password string whose length is between 1 and 7 characters (inclusive), the registration form SHALL reject the submission — no user account is created and the user count remains unchanged.

**Validates: Requirements 1.4**

---

### Property 4: Invalid email formats are always rejected

*For any* string that does not conform to a valid email address format (e.g., missing `@`, missing domain), the registration form SHALL reject the submission — no user account is created.

**Validates: Requirements 1.5**

---

### Property 5: Login with valid credentials always establishes the correct session

*For any* registered user (Admin or Adopter), submitting their correct email and password SHALL create an authenticated session and redirect the user to their role-appropriate home page — Admins to `/dashboard/`, Adopters to `/pets/`.

**Validates: Requirements 2.2, 2.4, 2.5**

---

### Property 6: Wrong credentials always return a generic error

*For any* email-and-password pair that does not match a registered account, the login attempt SHALL be rejected with a generic error message that does not reveal whether the email or the password was incorrect.

**Validates: Requirements 2.3**

---

### Property 7: Logout always invalidates the session

*For any* authenticated user, submitting a logout request SHALL invalidate the session such that any subsequent request requiring authentication redirects to the login page.

**Validates: Requirements 2.6**

---

### Property 8: Admin-only routes return 403 for any Adopter

*For any* registered Adopter user, a GET request to any URL under `/dashboard/` SHALL return a 403 Forbidden response without exposing any admin content.

**Validates: Requirements 2.9**

---

### Property 9: Pet browsing page only ever shows Available pets

*For any* database state containing pets with a mix of statuses (`available`, `adopted`, `pending`, `unavailable`), the browsing page SHALL only display pets whose status is `available`. No pet with any other status SHALL appear in the results.

**Validates: Requirements 3.1, 3.2**

---

### Property 10: Pagination never exceeds 12 items per page, and filters persist across pages

*For any* number of available pets N greater than 12, and *for any* active filter state, each individual page of results SHALL display at most 12 pet listing cards, and all cards on that page SHALL still match the active filter criteria.

**Validates: Requirements 3.5, 3.6**

---

### Property 11: Filter results always match all applied criteria

*For any* combination of filter values (species, breed, age range, gender, size, location, search text), every pet returned in the filtered results SHALL match ALL of the applied criteria simultaneously. No pet that fails any single criterion SHALL appear in the results.

**Validates: Requirements 4.2, 4.3**

---

### Property 12: Clearing all filters restores the complete available pet list

*For any* filter state, clearing all filter criteria SHALL produce a result set that is identical to the unfiltered list of all available pets — no more, no fewer.

**Validates: Requirements 4.4**

---

### Property 13: Pet profile page always contains all required fields

*For any* pet record in the database, requesting its profile page SHALL return an HTML response that contains the pet's name, species, breed, age, gender, size, health status, temperament, compatibility notes, location, and date listed.

**Validates: Requirements 5.2**

---

### Property 14: Existing applicants see status instead of the Apply button

*For any* Adopter who has already submitted an Adoption Application for a specific pet, viewing that pet's profile page SHALL display the current Application Status and SHALL NOT display the "Apply to Adopt" button.

**Validates: Requirements 5.7**

---

### Property 15: Valid adoption application always creates a Pending record

*For any* authenticated Adopter who has not previously applied for a specific pet, submitting a complete and valid adoption application form SHALL create exactly one `AdoptionApplication` record with `status = 'pending'` and SHALL send one confirmation email to the applicant's registered email address.

**Validates: Requirements 6.3, 6.6**

---

### Property 16: Incomplete application forms are always rejected

*For any* adoption application submission that has one or more required fields left empty, the form SHALL be rejected — no `AdoptionApplication` record is created and the total application count remains unchanged.

**Validates: Requirements 6.4**

---

### Property 17: Duplicate applications are always blocked

*For any* Adopter-and-Pet pair for which an `AdoptionApplication` already exists, a second application submission for the same pair SHALL be rejected — exactly one application record for that pair SHALL ever exist in the database.

**Validates: Requirements 6.5**

---

### Property 18: My Applications page shows exactly the logged-in Adopter's applications

*For any* authenticated Adopter, the "My Applications" page SHALL display exactly all applications submitted by that Adopter — no applications from other adopters, and no applications from that adopter are omitted.

**Validates: Requirements 7.2**

---

### Property 19: Status change to Approved or Rejected always triggers a notification email

*For any* `AdoptionApplication`, when its status is updated to `Approved` or `Rejected` by an Admin, exactly one notification email SHALL be sent to the applicant's registered email address containing the new status.

**Validates: Requirements 7.5**

---

### Property 20: Admin pet management lists all pets regardless of status

*For any* database state, the admin pet management section at `/dashboard/pets/` SHALL display all pet records regardless of their adoption status — no pet record is hidden from the admin view.

**Validates: Requirements 8.1**

---

### Property 21: Valid pet submissions always create an Available pet

*For any* valid "Add Pet" form submission containing all required fields and at least one valid image, a new `Pet` record SHALL be created with `status = 'available'`.

**Validates: Requirements 8.2**

---

### Property 22: Valid image uploads are always accepted; oversized uploads are always rejected

*For any* image file that is a JPEG, PNG, or WebP with a file size of 5 MB or less, the upload SHALL succeed and the image SHALL be saved to `MEDIA_ROOT`. *For any* image file whose size exceeds 5 MB, the upload SHALL be rejected and no file SHALL be saved.

**Validates: Requirements 8.5, 8.6**

---

### Property 23: Marking a pet as Adopted removes it from browsing and rejects its pending applications

*For any* pet that is marked as `Adopted` by an Admin, that pet SHALL no longer appear on the public browsing page, and all associated `AdoptionApplication` records with status `Pending` or `Under Review` SHALL be updated to reflect the outcome.

**Validates: Requirements 8.7**

---

### Property 24: Deleting a pet cascades to all associated photos and applications

*For any* pet record that has N photos and M adoption applications, deleting the pet record SHALL result in exactly 0 `PetPhoto` records and exactly 0 `AdoptionApplication` records remaining for that pet in the database.

**Validates: Requirements 8.8**

---

### Property 25: Approving an application sets the pet to Adopted and rejects all competing applications

*For any* `AdoptionApplication` that is approved by an Admin, the following three conditions SHALL all hold simultaneously: (1) the approved application's status is set to `Approved`, (2) the associated pet's status is set to `Adopted`, and (3) every other application for the same pet whose status is `Pending` or `Under Review` is set to `Rejected`.

**Validates: Requirements 9.5**

---

### Property 26: Rejection requires a non-empty rejection reason

*For any* attempt to reject an `AdoptionApplication`, the rejection SHALL only be saved if `admin_remarks` is non-empty. An attempt to reject without providing a reason SHALL be rejected by the form and the application status SHALL remain unchanged.

**Validates: Requirements 9.6**

---

### Property 27: Deactivating an account blocks login; reactivating restores it

*For any* Adopter account, after an Admin deactivates it, any login attempt with that account's credentials SHALL be blocked with a deactivation message. After the same account is reactivated by an Admin, a login attempt with the same credentials SHALL succeed and establish a valid session.

**Validates: Requirements 10.2, 10.3**

---

### Property 28: Valid surrender submissions always create a record and notify the Admin

*For any* complete surrender form submission with all required fields filled in, a `SurrenderRequest` record SHALL be created with `status = 'new'`, and exactly one notification email SHALL be sent to the Admin's registered email address.

**Validates: Requirements 11.3, 11.5**

---

### Property 29: Incomplete surrender forms are always rejected

*For any* surrender form submission with one or more required fields left empty, the form SHALL be rejected — no `SurrenderRequest` record is created.

**Validates: Requirements 11.4**

---

### Property 30: Dashboard summary stats always reflect actual database counts

*For any* database state, the summary statistics displayed on the Admin Dashboard home page SHALL equal the actual counts of the corresponding records in the database — total pets, available pets, pending applications, registered adopters, and new surrender requests.

**Validates: Requirements 12.1**

---

### Property 31: XSS payloads in pet data are always escaped in rendered HTML

*For any* pet record whose text fields (name, description, breed, etc.) contain HTML special characters or script tags, the rendered profile page HTML SHALL escape those characters such that they are displayed as literal text and no injected HTML elements are executed.

**Validates: Requirements 15.3**

---

### Property 32: Rate limit blocks login after 5 consecutive failures

*For any* IP address that has made 5 consecutive failed login attempts within a 15-minute window, the 6th login attempt from that IP SHALL be blocked with a rate-limit message — the credentials SHALL NOT be checked and no session SHALL be created.

**Validates: Requirements 15.5, 15.6**

---
