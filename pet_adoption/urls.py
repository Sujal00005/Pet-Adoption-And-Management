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


def home_view(request):
    """
    Landing page with hero section and featured pets.
    """
    from django.shortcuts import render
    from pets.models import Pet
    from accounts.models import UserProfile
    
    # Get featured pets (latest 6 available)
    featured_pets = (
        Pet.objects.filter(status='available')
        .prefetch_related('photos')
        .order_by('-listed_at')[:6]
    )
    
    # Stats for hero section
    stats = {
        'total_pets': Pet.objects.filter(status='available').count(),
        'total_adoptions': Pet.objects.filter(status='adopted').count(),
        'total_adopters': UserProfile.objects.filter(role='adopter').count(),
    }
    
    return render(request, 'home.html', {
        'featured_pets': featured_pets,
        'stats': stats,
    })


urlpatterns = [
    # Django's built-in admin site (useful for development; restrict in production)
    path('admin/', admin.site.urls),

    # Portal root — home page
    path('', home_view, name='home'),

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
