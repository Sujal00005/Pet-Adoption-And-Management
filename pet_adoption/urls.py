"""
Root URL configuration for the Pet Adoption and Rescue Management Portal.

Each Django app owns its own urls.py; we just include them here under
their respective path prefixes. The root path '/' redirects to the right
home page depending on the visitor's authentication state and role.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from pet_adoption.error_views import handler_403, handler_404, handler_500


# ---------------------------------------------------------------------------
# Custom error handlers — Django looks for these at module level in ROOT_URLCONF
# ---------------------------------------------------------------------------

handler403 = handler_403
handler404 = handler_404
handler500 = handler_500


def root_redirect(request):
    """
    Redirect visitors to the appropriate home page.

    - Authenticated admin  → Admin dashboard
    - Authenticated adopter → Pet browsing page
    - Anonymous visitor    → Pet browsing page (no account needed to browse)
    """
    if request.user.is_authenticated:
        # Check the user's role stored in their profile
        try:
            if request.user.profile.role == 'admin':
                return redirect('/dashboard/')
        except AttributeError:
            # Profile doesn't exist yet — treat as adopter
            pass
    # Adopters and anonymous visitors both land on the pet browsing page
    return redirect('/pets/')


urlpatterns = [
    # Django's built-in admin site (useful for development; restrict in production)
    path('admin/', admin.site.urls),

    # Portal root — smart redirect based on role
    path('', root_redirect, name='root'),

    # App URL namespaces
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('pets/',      include('pets.urls',      namespace='pets')),
    path('adoptions/', include('adoptions.urls', namespace='adoptions')),
    path('surrender/', include('surrenders.urls', namespace='surrenders')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

# Serve uploaded media files during development only.
# In production, configure your web server (nginx/Apache) to serve MEDIA_ROOT.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
