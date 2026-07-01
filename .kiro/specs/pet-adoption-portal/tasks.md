# Implementation Plan: Pet Adoption and Rescue Management Portal

## Overview

Build the portal incrementally using Django 4.x (Python), SQLite, plain HTML/CSS, and vanilla JavaScript. All views are function-based. No external JS/CSS libraries. Tasks are ordered so each builds on the previous with no circular dependencies.

## Tasks

- [x] 1. Project Setup and Configuration
  - [x] 1.1 Create the Django project and app skeletons
    - Run `django-admin startproject pet_adoption .` inside the project root
    - Create apps: `python manage.py startapp accounts`, `pets`, `adoptions`, `surrenders`, `dashboard`
    - Create the `notifications/` package directory with `__init__.py` and `emails.py`
    - Create top-level directories: `templates/`, `static/css/`, `media/`
    - Create `requirements.txt` pinning `Django==4.2.*` and `Pillow==10.*`
    - _Requirements: 14.1_

  - [x] 1.2 Configure `settings.py`
    - Add all five apps to `INSTALLED_APPS`
    - Set `TEMPLATES` `DIRS` to include the project-level `templates/` folder
    - Configure `MEDIA_ROOT`, `MEDIA_URL`, `STATIC_ROOT`, `STATIC_URL`
    - Set `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`
    - Add Gmail SMTP settings (`EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`) — read from environment variables using `os.environ.get`
    - Set `SESSION_COOKIE_AGE = 3600` (60-minute session expiry per Requirement 2.8)
    - _Requirements: 2.8, 14.4, 15.2_

  - [x] 1.3 Set up root URL configuration and shared error templates
    - Edit `pet_adoption/urls.py` to include each app's `urls.py` under its prefix, and serve `MEDIA_ROOT` in development via `static()`
    - Add a root redirect view (anonymous → `/pets/`, admin → `/dashboard/`, adopter → `/pets/`)
    - Create `templates/403.html`, `templates/404.html`, `templates/500.html` with a basic "oops" message that extends `base.html`
    - Register the custom error handlers in `pet_adoption/urls.py` (`handler403`, `handler404`, `handler500`)
    - _Requirements: 2.4, 2.5, 2.9_


- [x] 2. Base Templates and Shared Static Assets
  - [x] 2.1 Create `templates/base.html` and `templates/navbar.html`
    - Write `base.html` with semantic HTML5 skeleton (`<html>`, `<head>`, `<body>`), blocks for `title`, `extra_head`, `content`, `extra_scripts`, and a `{% include "navbar.html" %}`
    - Write `navbar.html` with conditional rendering: unauthenticated → logo + Login/Register links; Adopter → logo + Pets + My Applications + Surrender + Logout; Admin → logo + Dashboard + Logout
    - Link `static/css/style.css` in `<head>` using `{% static %}`
    - _Requirements: 13.2, 13.6_

  - [x] 2.2 Write `static/css/style.css` — base layout and typography
    - CSS reset, root CSS variables for colours (primary, accent, error, background, surface), and typography (font family, sizes, line-height)
    - Global styles for `body`, `a`, `button`, `input`, `select`, `textarea`, `label`
    - Navbar styles (horizontal flex layout, logo, nav links, user info, logout)
    - Utility classes: `.container`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.error-msg`, `.success-banner`, `.form-group`
    - Ensure a minimum 4.5:1 colour contrast ratio for all body text
    - _Requirements: 13.1, 13.4, 13.5_


- [x] 3. Database Models
  - [x] 3.1 Create `accounts/models.py` — `UserProfile` model
    - Define `UserProfile` with `OneToOneField(User)`, `role` (choices: admin/adopter), `phone`, `created_at`
    - Write a `post_save` signal on `User` in `accounts/apps.py` (`ready()`) that auto-creates a linked `UserProfile` on user creation
    - Register `UserProfile` in `accounts/admin.py`
    - Run `python manage.py makemigrations accounts`
    - _Requirements: 1.2, 14.1, 14.2_

  - [x] 3.2 Create `pets/models.py` — `Pet` and `PetPhoto` models
    - Define `Pet` with all fields from the design: `name`, `species`, `breed`, `age_years`, `age_months`, `gender`, `size`, `color_markings`, `description`, `temperament`, `good_with_kids`, `good_with_pets`, `is_vaccinated`, `is_neutered`, `medical_notes`, `location`, `status`, `listed_at`, `updated_at`, `added_by`
    - Add `age_display` property and `primary_photo` property
    - Define `PetPhoto` with `pet` FK, `image` (ImageField using `pet_photo_upload_path`), `caption`, `is_primary`, `uploaded_at`
    - Register both in `pets/admin.py`
    - Run `python manage.py makemigrations pets`
    - _Requirements: 5.2, 8.2, 14.1, 14.2_

  - [x] 3.3 Create `adoptions/models.py` — `AdoptionApplication` model
    - Define `AdoptionApplication` with all fields from the design, `unique_together = [('pet', 'applicant')]`, status choices, and `reviewed_at` timestamp
    - Register in `adoptions/admin.py`
    - Run `python manage.py makemigrations adoptions`
    - _Requirements: 6.3, 6.5, 14.1, 14.2_

  - [x] 3.4 Create `surrenders/models.py` — `SurrenderRequest` model
    - Define `SurrenderRequest` with all fields from the design: submitter info, pet info, `status` (new/reviewed), `admin_notes`, `submitted_at`, `reviewed_at`
    - Register in `surrenders/admin.py`
    - Run `python manage.py makemigrations surrenders`
    - Run `python manage.py migrate` to apply all migrations
    - _Requirements: 11.3, 14.1_


- [x] 4. Authentication — `accounts` app
  - [x] 4.1 Create `accounts/decorators.py` and `accounts/forms.py`
    - Write `admin_required` decorator: checks `request.user.is_authenticated` and `request.user.profile.role == 'admin'`; raises `PermissionDenied` otherwise
    - Write `adopter_required` decorator: redirects unauthenticated users to login
    - Write `AdopterRegistrationForm` (fields: `email`, `first_name`, `last_name`, `phone`, `password1`, `password2`) with `clean_email` checking uniqueness, `clean_password1` enforcing minimum 8 characters, and `clean` matching passwords
    - Write `LoginForm` (fields: `email`, `password`)
    - _Requirements: 1.3, 1.4, 1.5, 2.9_

  - [x] 4.2 Create `accounts/views.py` — registration, login, logout
    - Write `register_view`: GET → render `accounts/register.html`; POST → validate `AdopterRegistrationForm`, create `User` (email as username), set `profile.role = 'adopter'`, redirect to login with success message
    - Write `login_view`: GET → render `accounts/login.html`; POST → `authenticate()`, create session, redirect by role (admin → `/dashboard/`, adopter → `/pets/`); show generic error on failure (never reveal which field is wrong)
    - Write `logout_view`: POST only, `auth.logout(request)`, redirect to login page
    - _Requirements: 1.2, 1.7, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 4.3 Create `accounts/urls.py` and wire templates
    - Define URL patterns: `register/`, `login/`, `logout/`
    - Create `templates/accounts/register.html` — registration form with inline field errors via `{{ form.field.errors }}`
    - Create `templates/accounts/login.html` — email + password form with non-field error banner
    - _Requirements: 1.1, 2.1_

  - [ ]* 4.4 Write property tests for authentication (Properties 1–8)
    - **Property 1: Valid registration always creates an Adopter account** — POST valid unique data, assert `User.objects.count()` increments by 1 and `profile.role == 'adopter'`
    - **Property 2: Duplicate email registration is always rejected** — register same email twice, assert count unchanged on second attempt
    - **Property 3: Short passwords are always rejected** — parametrize passwords of length 1–7, assert no user created
    - **Property 4: Invalid email formats are always rejected** — test strings without `@`, without domain; assert no user created
    - **Property 5: Login redirects by role** — login as admin → assert redirect to `/dashboard/`; login as adopter → assert redirect to `/pets/`
    - **Property 6: Wrong credentials return generic error** — assert response contains no "email" or "password" field hint
    - **Property 7: Logout invalidates session** — login, logout, GET protected page → assert redirect to login
    - **Property 8: Admin routes return 403 for Adopters** — login as adopter, GET `/dashboard/` → assert status 403
    - _Validates: Requirements 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4, 2.5, 2.6, 2.9_


- [x] 5. Pet Browsing and Profiles — `pets` app
  - [x] 5.1 Create `pets/forms.py` — `PetFilterForm` and `PetPhotoForm`
    - Write `PetFilterForm` (unbound, GET-based): fields for `species`, `breed`, `min_age_years`, `max_age_years`, `gender`, `size`, `location`, `q` (text search); all fields optional
    - Write `PetPhotoForm` with `clean_image()` validating file size ≤ 5 MB and content type in `['image/jpeg', 'image/png', 'image/webp']`
    - _Requirements: 4.1, 8.5, 8.6_

  - [x] 5.2 Create `pets/views.py` — public browsing and pet detail views
    - Write `pet_list_view` (no auth required): query `Pet.objects.filter(status='available')`; apply filters from `PetFilterForm`; paginate at 12 per page using `Django Paginator`; preserve query params in pagination links; render `pets/browse.html`
    - Write `pet_detail_view` (no auth required): `get_object_or_404(Pet, pk=pk)`; fetch all `PetPhoto` objects; check if current user has an existing application for this pet; render `pets/detail.html`
    - _Requirements: 3.1, 3.2, 3.5, 3.6, 4.2, 4.3, 4.4, 5.1, 5.2, 5.5, 5.6, 5.7_

  - [x] 5.3 Create `pets/urls.py` and templates
    - URL patterns: `""` → `pet_list_view`, `"<int:pk>/"` → `pet_detail_view`
    - Create `templates/pets/browse.html`: filter sidebar (species, breed, age range, gender, size, location, text search), responsive card grid (12-per-page), pagination controls, "no pets available" / "no results" messages
    - Create `templates/pets/detail.html`: full pet info, photo gallery with previous/next controls (vanilla JS), conditional "Apply to Adopt" button, application status badge, login prompt for unauthenticated visitors
    - _Requirements: 3.2, 3.3, 3.4, 4.5, 4.6, 5.3, 5.4, 5.6_

  - [ ]* 5.4 Write property tests for pet browsing (Properties 9–13)
    - **Property 9: Browsing page only shows Available pets** — seed DB with pets of all statuses, assert only `available` ones appear in response
    - **Property 10: Pagination shows at most 12 items and filters persist** — create 25 available pets, apply species filter, check every page has ≤ 12 cards and all match species
    - **Property 11: Filter results always match all applied criteria** — create diverse pets, apply multi-criteria filter, assert every returned pet matches all criteria
    - **Property 12: Clearing filters restores full available list** — apply filter, then request with no filter params, assert count equals total available pets
    - **Property 13: Pet profile page contains all required fields** — create a pet, GET detail URL, assert HTML contains name, species, breed, age, gender, size, health status, temperament, location
    - _Validates: Requirements 3.1, 3.2, 3.5, 3.6, 4.2, 4.3, 4.4, 5.2_


- [x] 6. Adoption Applications — `adoptions` app
  - [x] 6.1 Create `adoptions/forms.py` — `AdoptionApplicationForm`
    - Fields: `full_name` (pre-fill from profile), `phone`, `address`, `housing_type`, `owns_or_rents`, `landlord_contact` (optional if owns), `household_members`, `has_other_pets`, `other_pets_desc`, `prev_pet_experience`, `reason_for_adoption`, `agrees_to_home_visit`
    - `clean()` method: if `owns_or_rents == 'rents'` and `landlord_contact` is empty, raise `ValidationError`; if `agrees_to_home_visit` is False, raise `ValidationError`
    - _Requirements: 6.2, 6.4_

  - [x] 6.2 Create `adoptions/views.py` — application submission and "My Applications"
    - Write `apply_view` (`@adopter_required`): GET → render pre-filled form; POST → validate, check for existing application (return error if duplicate), create `AdoptionApplication(status='pending')`, call `send_application_confirmation()`, redirect with success message
    - Write `my_applications_view` (`@adopter_required`): query `AdoptionApplication.objects.filter(applicant=request.user)`, render `adoptions/my_applications.html`
    - Write `application_detail_view` (`@adopter_required`): fetch application owned by request.user, render `adoptions/application_detail.html`
    - _Requirements: 6.1, 6.3, 6.5, 6.6, 7.1, 7.2, 7.3_

  - [x] 6.3 Create `adoptions/urls.py` and templates
    - URL patterns: `apply/<int:pet_pk>/`, `my-applications/`, `<int:pk>/`
    - Create `templates/adoptions/apply.html`: full application form with field error display
    - Create `templates/adoptions/my_applications.html`: table/card list of applications (pet photo, pet name, date, status badge)
    - Create `templates/adoptions/application_detail.html`: all submitted form data, current status, admin remarks (if any)
    - _Requirements: 6.1, 7.1, 7.2, 7.3_

  - [ ]* 6.4 Write property tests for adoption applications (Properties 14–18)
    - **Property 14: Existing applicants see status instead of Apply button** — create application, GET pet detail as that adopter, assert "Apply to Adopt" absent and status badge present
    - **Property 15: Valid application creates a Pending record and sends confirmation email** — POST valid form, assert `AdoptionApplication.objects.count()` increments, `status='pending'`, and `len(mail.outbox) == 1`
    - **Property 16: Incomplete application forms are rejected** — POST with each required field individually blank, assert no record created
    - **Property 17: Duplicate applications are blocked** — submit same adopter+pet twice, assert `IntegrityError` handled gracefully and count stays at 1
    - **Property 18: My Applications page shows only the logged-in adopter's applications** — create applications for two adopters, login as one, assert only that user's applications appear
    - _Validates: Requirements 5.7, 6.3, 6.4, 6.5, 6.6, 7.2_


- [x] 7. Surrender Form — `surrenders` app
  - [x] 7.1 Create `surrenders/forms.py` — `SurrenderRequestForm`
    - Fields: `submitter_name`, `submitter_phone`, `submitter_email`, `pet_name`, `species`, `breed` (optional), `approximate_age` (optional), `gender`, `reason`, `is_vaccinated`, `health_notes` (optional)
    - All required fields validated; email format validated by `EmailField`
    - _Requirements: 11.2, 11.4_

  - [x] 7.2 Create `surrenders/views.py` — public surrender form and success page
    - Write `surrender_form_view` (no auth required): GET → render `surrenders/form.html`; POST → validate, create `SurrenderRequest(status='new')`, call `send_surrender_notification_to_admin()`, redirect to `surrender/success/`
    - Write `surrender_success_view`: render `surrenders/success.html` with 2–3 business day message
    - _Requirements: 11.1, 11.3, 11.5_

  - [x] 7.3 Create `surrenders/urls.py` and templates
    - URL patterns: `""` → `surrender_form_view`, `"success/"` → `surrender_success_view`
    - Create `templates/surrenders/form.html`: full surrender form, required field indicators, error display
    - Create `templates/surrenders/success.html`: confirmation message with estimated response timeframe
    - _Requirements: 11.1, 11.3_

  - [ ]* 7.4 Write property tests for surrender form (Properties 28–29)
    - **Property 28: Valid surrender submission creates a record and notifies admin** — POST complete valid form, assert `SurrenderRequest.objects.count()` increments, `status='new'`, and `len(mail.outbox) == 1`
    - **Property 29: Incomplete surrender forms are rejected** — POST with each required field blank, assert no record created
    - _Validates: Requirements 11.3, 11.4, 11.5_


- [x] 8. Admin Dashboard — `dashboard` app and admin views in other apps
  - [x] 8.1 Create `dashboard/views.py` — dashboard home, user management
    - Write `dashboard_home_view` (`@admin_required`): aggregate stats using ORM — total pets, available pets, pending applications, total adopters, new surrender requests; query last 10 activity events (applications, status changes, registrations, surrenders) ordered by timestamp; render `dashboard/home.html`
    - Write `user_list_view` (`@admin_required`): query all `UserProfile` objects with `role='adopter'`, annotate with application count; render `dashboard/users_list.html`
    - Write `user_detail_view` (`@admin_required`): fetch user + all their applications; support POST to toggle `user.is_active`; render `dashboard/user_detail.html`
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 12.1, 12.2_

  - [x] 8.2 Create admin pet management views in `pets/views.py`
    - Write `admin_pet_list_view` (`@admin_required`): query ALL pets (all statuses); render `dashboard/pets_list.html`
    - Write `admin_pet_add_view` (`@admin_required`): `PetForm` for adding a pet; on POST validate and save `Pet` with `status='available'` and `added_by=request.user`; also save uploaded photo via `PetPhotoForm`
    - Write `admin_pet_edit_view` (`@admin_required`): pre-fill `PetForm`; on POST update the pet record; support marking as `Adopted` which calls `_mark_pet_adopted(pet)` helper (updates pet status, rejects pending applications)
    - Write `admin_pet_delete_view` (`@admin_required`): confirm prompt; on POST delete pet (cascade handles photos and applications); redirect to pet list
    - Create `pets/forms.py` `PetForm`: all Pet fields, with `PetPhotoForm` included for photo upload
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [x] 8.3 Create admin application management views in `adoptions/views.py`
    - Write `admin_applications_list_view` (`@admin_required`): query all applications; support filter by `status`, `pet_name` (icontains), `date_from`, `date_to` via GET params; annotate pending count for nav badge; render `dashboard/applications_list.html`
    - Write `admin_application_review_view` (`@admin_required`): fetch application; handle three POST actions: `set_under_review` (update status + timestamp), `approve` (wrap in `transaction.atomic()` — approve application, set pet to adopted, bulk-reject competing applications, call email helper), `reject` (require non-empty `admin_remarks`, update status, call email helper)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [x] 8.4 Create admin surrender management views in `surrenders/views.py`
    - Write `admin_surrender_list_view` (`@admin_required`): query all surrender requests ordered by `submitted_at` desc; render `dashboard/surrenders_list.html`
    - Write `admin_surrender_detail_view` (`@admin_required`): fetch surrender request; handle POST to mark as `Reviewed` and save `admin_notes`; update `reviewed_at` timestamp
    - _Requirements: 11.6, 11.7_

  - [x] 8.5 Create `dashboard/urls.py` and all dashboard templates
    - Define URL patterns for all dashboard routes (home, pets CRUD, applications, users, surrenders)
    - Create `templates/dashboard/home.html`: stats cards (total pets, available, pending apps, adopters, new surrenders) with click-through links; recent activity feed (last 10 events)
    - Create `templates/dashboard/pets_list.html`: table of all pets, add/edit/delete actions
    - Create `templates/dashboard/pet_form.html`: shared add/edit form with photo upload input
    - Create `templates/dashboard/applications_list.html`: filterable table with status badges; pending count badge in nav
    - Create `templates/dashboard/application_review.html`: full application data + applicant info + pet summary + status action buttons
    - Create `templates/dashboard/users_list.html`: table of adopters with name, email, registration date, app count, activate/deactivate toggle
    - Create `templates/dashboard/user_detail.html`: user info + all their applications list
    - Create `templates/dashboard/surrenders_list.html`: table of surrenders with status badges
    - Create `templates/dashboard/surrender_detail.html`: full surrender details + mark as reviewed form
    - _Requirements: 8.1, 9.1, 9.7, 10.1, 10.4, 11.6, 12.1, 12.2, 12.3_

  - [ ]* 8.6 Write property tests for admin features (Properties 19–27, 30)
    - **Property 19: Status Approved/Rejected always triggers notification email** — approve and reject applications, assert `mail.outbox` receives exactly one email each time
    - **Property 20: Admin pet list shows all pets regardless of status** — create pets with all statuses, GET `/dashboard/pets/`, assert all appear
    - **Property 21: Valid pet form creates an Available pet** — POST valid pet data, assert `Pet.objects.last().status == 'available'`
    - **Property 22: Image validation — valid ≤5MB accepted, >5MB rejected** — test with mock file objects of varying sizes; assert valid saves and invalid raises `ValidationError`
    - **Property 23: Marking pet Adopted removes from browsing and rejects pending applications** — create pet + pending applications, mark adopted, GET `/pets/`, assert pet absent; assert applications status `'rejected'`
    - **Property 24: Deleting a pet cascades to photos and applications** — create pet with 3 photos and 2 applications, delete pet, assert `PetPhoto.objects.count() == 0` and `AdoptionApplication.objects.count() == 0`
    - **Property 25: Approving application sets pet Adopted and rejects competing applications** — create 3 applications for same pet, approve one, assert pet status `'adopted'`, other two status `'rejected'`
    - **Property 26: Rejection requires non-empty reason** — POST reject with empty `admin_remarks`, assert status unchanged
    - **Property 27: Deactivating blocks login; reactivating restores it** — deactivate, attempt login → assert failure; reactivate, attempt login → assert success
    - **Property 30: Dashboard stats equal actual DB counts** — seed DB, GET `/dashboard/`, parse stat values from response, compare to ORM counts
    - _Validates: Requirements 7.5, 8.1, 8.2, 8.5, 8.6, 8.7, 8.8, 9.5, 9.6, 10.2, 10.3, 12.1_


- [x] 9. Checkpoint — Core functionality complete
  - Ensure all migrations are applied, the development server starts without errors, all views return expected responses, and all non-optional tests pass. Ask the user if any questions arise before proceeding.

- [x] 10. Email Notifications — `notifications` module
  - [x] 10.1 Implement `notifications/emails.py`
    - Write `send_application_confirmation(application)`: email to `application.applicant.email`; subject `"Application Received — {pet_name}"`; body includes pet name, submission date, portal link; wrapped in `try/except` with `logger.exception()` on failure (non-fatal)
    - Write `send_application_status_update(application)`: email to applicant; subject `"Your Application for {pet_name} has been {status}"`; body includes status, admin remarks if any, portal link; only called when status is `'approved'` or `'rejected'`
    - Write `send_surrender_notification_to_admin(surrender)`: email to `settings.ADMIN_EMAIL`; subject `"New Surrender Request — {pet_name}"`; body includes full surrender request details; wrapped in `try/except`
    - _Requirements: 6.6, 7.5, 11.5_

  - [ ]* 10.2 Write property tests for email notifications (Property 19, 28)
    - **Property 19 (re-verify with real email function)**: call `send_application_status_update()` for approved and rejected applications, assert `mail.outbox` count and subject content
    - **Property 28 (re-verify)**: call `send_surrender_notification_to_admin()`, assert admin email received with pet name in subject
    - Use Django's `django.test.override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')` to capture outbox
    - _Validates: Requirements 6.6, 7.5, 11.5_


- [x] 11. Rate Limiting for Login
  - [x] 11.1 Implement login rate limiting in `accounts/views.py`
    - In `login_view`, track failed attempts per IP using Django's cache framework (`django.core.cache.cache`) with key `f"login_attempts_{ip_address}"` and TTL of 900 seconds (15 minutes)
    - On each failed login, increment the counter; if counter ≥ 5, block the attempt and render the login template with a `rate_limited=True` context variable and message "Too many failed attempts. Please try again in 15 minutes."
    - On successful login, delete the cache key to reset the counter
    - Helper function `get_client_ip(request)` reads `HTTP_X_FORWARDED_FOR` or `REMOTE_ADDR`
    - _Requirements: 15.5, 15.6_

  - [ ]* 11.2 Write property test for rate limiting (Property 32)
    - **Property 32: Rate limit blocks login after 5 consecutive failures** — POST 5 bad-credential login attempts from a fixed `REMOTE_ADDR`, then POST a 6th with correct credentials; assert the 6th response contains the rate-limit message and no session is created
    - _Validates: Requirements 15.5, 15.6_


- [x] 12. Frontend Polish — CSS and JavaScript
  - [x] 12.1 Extend `static/css/style.css` — responsive grid and card styles
    - Pet listing card styles: photo aspect ratio, name, species, age, location, hover effect
    - Responsive grid: 3 columns on desktop (≥1024px), 2 on tablet (≥600px), 1 on mobile (<600px) using CSS Grid / `auto-fill`
    - Filter sidebar: collapsible on mobile (toggle button shows/hides), always visible on desktop
    - Pagination controls: centred, with active page highlight
    - Status badges: colour-coded (Pending = yellow, Under Review = blue, Approved = green, Rejected = red)
    - Admin dashboard stats cards: flex row, icon + number + label, hover lift
    - _Requirements: 3.3, 13.1, 13.3, 13.4_

  - [x] 12.2 Write `static/js/pets.js` — photo gallery and breed filter
    - Photo gallery: on `pets/detail.html`, find all `<img data-gallery>` elements; render previous/next arrow buttons via JS; clicking an arrow swaps the visible image (no page reload)
    - Breed filter: on `pets/browse.html`, listen for `change` event on the species `<select>`; fetch breed options from a `data-breeds` JSON attribute on the select element (rendered server-side); update the breed `<select>` options dynamically without a page reload
    - Add `alt` text data to gallery images passed from the template context
    - _Requirements: 4.6, 5.3, 5.4, 13.3_

  - [x] 12.3 Write `static/js/forms.js` — client-side form UX enhancements
    - Inline character counter for `<textarea>` fields with `maxlength` attribute
    - Show/hide `landlord_contact` field in the adoption application form based on the current value of `owns_or_rents` select
    - Confirm dialog before submitting delete forms (`<form data-confirm="Are you sure?">`)
    - Disable the submit button after first click to prevent double-submission
    - _Requirements: 6.2, 13.4_

  - [ ]* 12.4 Write property test for XSS escaping (Property 31)
    - **Property 31: XSS payloads in pet data are escaped in rendered HTML** — create a pet whose `name` is `<script>alert('xss')</script>`, GET detail page, assert the raw `<script>` tag does not appear in response content and `&lt;script&gt;` (or equivalent) does
    - _Validates: Requirements 15.3_


- [x] 13. Accessibility and Semantic HTML Audit
  - [x] 13.1 Audit and fix semantic HTML across all templates
    - Ensure every page uses `<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, `<article>` appropriately
    - Add `<label for="...">` for every form input
    - Add descriptive `alt` attributes to all `<img>` tags; use `alt=""` for purely decorative images
    - Add `aria-label` or `aria-describedby` to icon-only buttons (gallery arrows, delete icons)
    - Add `tabindex` and `:focus` CSS styles to all interactive elements to ensure keyboard navigability
    - _Requirements: 13.2, 13.3, 13.4_

  - [x] 13.2 Add `<meta>` viewport tag and test responsive breakpoints
    - Add `<meta name="viewport" content="width=device-width, initial-scale=1">` to `base.html`
    - Verify layout renders correctly at 320px, 768px, 1024px, and 1440px by inspecting the CSS grid/flex media queries
    - _Requirements: 13.1_

- [x] 14. Final Checkpoint — All tests pass, full integration verified
  - Run `python manage.py test` — all tests must pass
  - Manually verify: registration → login → browse → apply flow end-to-end
  - Manually verify: surrender form submission → admin receives email → admin marks reviewed
  - Manually verify: admin approves application → pet marked Adopted → competing applications rejected → adopter receives email
  - Ask the user if any questions arise.


## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP build
- The design document uses Python/Django throughout — no language selection required
- All tests use Django's built-in `TestCase` and `self.client`; email sending is tested via `mail.outbox` with the `locmem` backend
- Property tests validate universal correctness as defined in the design's Correctness Properties section
- `transaction.atomic()` is used for all multi-model writes (application approval, pet deletion cascade)
- Rate limiting uses Django's cache framework (`LocMemCache` in development; swap to Redis in production)
- `MEDIA_ROOT` / `MEDIA_URL` serving in development requires `settings.DEBUG = True` and the `urlpatterns += static(...)` line in `urls.py`
- Each task references specific requirements for traceability

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["2.1", "2.2", "3.1", "3.2", "3.3", "3.4"] },
    { "id": 2, "tasks": ["4.1", "4.2", "4.3", "5.1"] },
    { "id": 3, "tasks": ["4.4", "5.2"] },
    { "id": 4, "tasks": ["5.3", "6.1", "7.1"] },
    { "id": 5, "tasks": ["5.4", "6.2", "7.2"] },
    { "id": 6, "tasks": ["6.3", "7.3", "8.1"] },
    { "id": 7, "tasks": ["6.4", "7.4", "8.2", "8.3", "8.4"] },
    { "id": 8, "tasks": ["8.5"] },
    { "id": 9, "tasks": ["8.6", "10.1"] },
    { "id": 10, "tasks": ["10.2", "11.1"] },
    { "id": 11, "tasks": ["11.2", "12.1", "12.2", "12.3"] },
    { "id": 12, "tasks": ["12.4", "13.1", "13.2"] }
  ]
}
```
