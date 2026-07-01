"""
Admin dashboard views.

All views require the requesting user to have role == 'admin'.
The @admin_required decorator handles unauthenticated and non-admin cases.
"""

import logging

from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import admin_required
from accounts.models import UserProfile
from adoptions.models import AdoptionApplication
from pets.models import Pet
from surrenders.models import SurrenderRequest

logger = logging.getLogger(__name__)


@admin_required
def dashboard_home_view(request):
    """
    Main dashboard overview — shows key stats and recent activity feeds.
    """
    stats = {
        'total_pets':     Pet.objects.count(),
        'available_pets': Pet.objects.filter(status='available').count(),
        'pending_apps':   AdoptionApplication.objects.filter(status='pending').count(),
        'total_adopters': UserProfile.objects.filter(role='adopter').count(),
        'new_surrenders': SurrenderRequest.objects.filter(status='new').count(),
    }
    recent_apps = (
        AdoptionApplication.objects
        .select_related('pet', 'applicant')
        .order_by('-submitted_at')[:5]
    )
    recent_surrenders = SurrenderRequest.objects.order_by('-submitted_at')[:3]

    return render(request, 'dashboard/home.html', {
        'stats': stats,
        'recent_apps': recent_apps,
        'recent_surrenders': recent_surrenders,
        'pending_count': stats['pending_apps'],
    })


@admin_required
def user_list_view(request):
    """
    List all registered adopters with their application counts.
    """
    profiles = (
        UserProfile.objects
        .filter(role='adopter')
        .select_related('user')
        .annotate(app_count=Count('user__applications'))
        .order_by('-created_at')
    )
    return render(request, 'dashboard/users_list.html', {
        'profiles': profiles,
        'pending_count': AdoptionApplication.objects.filter(status='pending').count(),
    })


@admin_required
def user_detail_view(request, pk):
    """
    View and manage a single adopter account.
    POST with action='deactivate' or 'reactivate' toggles the account status.
    """
    profile = get_object_or_404(UserProfile, pk=pk, role='adopter')
    user = profile.user

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'{user.get_full_name()} has been deactivated.')
        elif action == 'reactivate':
            user.is_active = True
            user.save()
            messages.success(request, f'{user.get_full_name()} has been reactivated.')
        return redirect('dashboard:user_detail', pk=pk)

    applications = (
        AdoptionApplication.objects
        .filter(applicant=user)
        .select_related('pet')
        .order_by('-submitted_at')
    )
    return render(request, 'dashboard/user_detail.html', {
        'profile': profile,
        'user_obj': user,
        'applications': applications,
        'pending_count': AdoptionApplication.objects.filter(status='pending').count(),
    })
