"""
Django settings for the Pet Adoption and Rescue Management Portal.

For development use only. Before deploying to production:
  - Move SECRET_KEY to an environment variable.
  - Set DEBUG = False.
  - Update ALLOWED_HOSTS with the real domain.
  - Switch DATABASES to PostgreSQL (or keep SQLite for small deployments).
  - Ensure EMAIL credentials are stored in environment variables (already done below).
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Load .env file automatically (no extra packages needed)
#
# Create a file called  .env  next to manage.py and put your secrets there:
#   EMAIL_HOST_USER=you@gmail.com
#   EMAIL_HOST_PASSWORD=your-app-password
#   ADMIN_EMAIL=you@gmail.com
#
# Lines starting with # are comments and are ignored.
# ---------------------------------------------------------------------------

_env_file = BASE_DIR / '.env'
if _env_file.exists():
    with open(_env_file, encoding='utf-8') as _f:
        for _line in _f:
            _line = _line.strip()
            # Skip blank lines and comments
            if not _line or _line.startswith('#'):
                continue
            # Split on the first '=' only
            if '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())


# ---------------------------------------------------------------------------
# Security — keep the secret key out of version control in production
# ---------------------------------------------------------------------------

# TODO: Move to an environment variable before production deployment.
SECRET_KEY = 'django-dev-secret-key-change-me-before-production-xj7k2p9q#m!w@v'

# Never run with DEBUG = True in production — it exposes stack traces.
DEBUG = True

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")


# ---------------------------------------------------------------------------
# Application registry
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our portal apps
    'accounts',
    'pets',
    'adoptions',
    'surrenders',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pet_adoption.urls'


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Include the project-level templates/ folder so all apps can use base.html
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pet_adoption.wsgi.application'


# ---------------------------------------------------------------------------
# Database — SQLite for development; swap to PostgreSQL for production
# ---------------------------------------------------------------------------

import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}


# ---------------------------------------------------------------------------
# Password validation — Django defaults kept for now
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'

# Indian Standard Time — adjust if the portal is deployed elsewhere
TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------------
# Static files — served by Django in development; use a CDN/nginx in production
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'

# Tell Django where to look for extra static files (our hand-written CSS)
STATICFILES_DIRS = [BASE_DIR / 'static']

# Where collectstatic will collect static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ---------------------------------------------------------------------------
# Media files — uploaded pet photos land here
# ---------------------------------------------------------------------------

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# Authentication redirects
# ---------------------------------------------------------------------------

# Where to send unauthenticated users when they hit a @login_required view
LOGIN_URL = '/accounts/login/'

# Default landing page after a successful login (overridden per-role in login_view)
LOGIN_REDIRECT_URL = '/pets/'

# Where to send the user after logout
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Sessions expire after 60 minutes of inactivity (Requirement 2.8)
SESSION_COOKIE_AGE = 3600


# ---------------------------------------------------------------------------
# Email — Gmail SMTP, credentials read from environment variables
# ---------------------------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Set these in your shell / .env before running the server:
#   EMAIL_HOST_USER=you@gmail.com
#   EMAIL_HOST_PASSWORD=your-app-password
#   ADMIN_EMAIL=shelter-admin@example.com
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# The inbox that receives surrender notifications and admin alerts
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', EMAIL_HOST_USER)


# ---------------------------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Admin registration secret key
# TODO: Move to an environment variable before production deployment.
# ---------------------------------------------------------------------------

ADMIN_REGISTRATION_KEY = 'paws-and-hearts-admin-2025'
