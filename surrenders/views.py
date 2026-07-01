"""
Surrender request views — public form submission and admin management.
"""

import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import admin_required
from adoptions.models import AdoptionApplication
from notifications.emails import send_surrender_notification_to_admin

from .forms import SurrenderRequestForm
from .models import SurrenderRequest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public views
# ---------------------------------------------------------------------------

def surrender_form_view(request):
    """
    Public surrender request form — no login required.
    On successful submission, notifies the admin by email and redirects
    to the thank-you page.
    """
    if request.method == 'POST':
        form = SurrenderRequestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            surrender = SurrenderRequest.objects.create(
                submitter_name=data['submitter_name'],
                submitter_phone=data['submitter_phone'],
                submitter_email=data['submitter_email'],
                pet_name=data['pet_name'],
                species=data['species'],
                breed=data.get('breed', ''),
                approximate_age=data.get('approximate_age', ''),
                gender=data.get('gender', ''),
                reason=data['reason'],
                is_vaccinated=data.get('is_vaccinated', False),
                health_notes=data.get('health_notes', ''),
                status='new',
            )
            send_surrender_notification_to_admin(surrender)
            return redirect('surrenders:success')
    else:
        form = SurrenderRequestForm()

    return render(request, 'surrenders/form.html', {'form': form})


def surrender_success_view(request):
    """Thank-you page shown after a surrender request is submitted."""
    return render(request, 'surrenders/success.html')


# ---------------------------------------------------------------------------
# Admin views
# ---------------------------------------------------------------------------

@admin_required
def admin_surrender_list_view(request):
    """Dashboard list of all surrender requests, newest first."""
    surrenders = SurrenderRequest.objects.order_by('-submitted_at')
    pending_count = AdoptionApplication.objects.filter(status='pending').count()
    return render(request, 'dashboard/surrenders_list.html', {
        'surrenders': surrenders,
        'pending_count': pending_count,
    })


@admin_required
def admin_surrender_detail_view(request, pk):
    """
    View full details of a single surrender request.
    POST marks it as reviewed and saves optional admin notes.
    """
    surrender = get_object_or_404(SurrenderRequest, pk=pk)

    if request.method == 'POST':
        surrender.status = 'reviewed'
        surrender.reviewed_at = timezone.now()
        surrender.admin_notes = request.POST.get('admin_notes', '')
        surrender.save()
        messages.success(request, 'Surrender request marked as reviewed.')
        return redirect('dashboard:surrenders_list')

    pending_count = AdoptionApplication.objects.filter(status='pending').count()
    return render(request, 'dashboard/surrender_detail.html', {
        'surrender': surrender,
        'pending_count': pending_count,
    })
