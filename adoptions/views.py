"""
Adoption application views for adopters.

Admin review views are added in Task 8.3.
"""

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import adopter_required
from notifications.emails import send_application_confirmation
from pets.models import Pet

from .forms import AdoptionApplicationForm
from .models import AdoptionApplication


def _is_adopter(user):
    """Return True when the user is an authenticated adopter (not admin)."""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 'adopter'
    except AttributeError:
        return True


@adopter_required
def apply_view(request, pet_pk):
    """
    Display and process an adoption application for a specific pet.

    Only available pets can receive new applications. Duplicate submissions
    for the same adopter + pet pair are blocked before save.
    """
    if not _is_adopter(request.user):
        messages.error(request, 'Only registered adopters can submit applications.')
        return redirect('pets:browse')

    pet = get_object_or_404(Pet, pk=pet_pk, status='available')

    if AdoptionApplication.objects.filter(pet=pet, applicant=request.user).exists():
        messages.info(
            request,
            f'You have already applied to adopt {pet.name}. '
            f'Check My Applications for the current status.',
        )
        return redirect('adoptions:my_applications')

    if request.method == 'POST':
        form = AdoptionApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.pet = pet
            application.applicant = request.user
            application.status = 'pending'

            try:
                application.save()
            except IntegrityError:
                messages.error(
                    request,
                    f'You have already submitted an application for {pet.name}.',
                )
                return redirect('adoptions:my_applications')

            send_application_confirmation(application)
            messages.success(
                request,
                f'Your application to adopt {pet.name} has been submitted successfully!',
            )
            return redirect('adoptions:my_applications')
    else:
        form = AdoptionApplicationForm(initial={
            'full_name': request.user.get_full_name(),
            'phone': getattr(request.user.profile, 'phone', ''),
        })

    return render(request, 'adoptions/apply.html', {
        'form': form,
        'pet': pet,
    })


@adopter_required
def my_applications_view(request):
    """List all adoption applications submitted by the logged-in adopter."""
    applications = (
        AdoptionApplication.objects
        .filter(applicant=request.user)
        .select_related('pet')
        .prefetch_related('pet__photos')
    )

    return render(request, 'adoptions/my_applications.html', {
        'applications': applications,
    })


@adopter_required
def application_detail_view(request, pk):
    """Show full details for one application owned by the logged-in adopter."""
    application = get_object_or_404(
        AdoptionApplication.objects.select_related('pet').prefetch_related('pet__photos'),
        pk=pk,
        applicant=request.user,
    )

    return render(request, 'adoptions/application_detail.html', {
        'application': application,
    })


# ---------------------------------------------------------------------------
# Admin application management views — added in Task 8.3
# ---------------------------------------------------------------------------

from django.db import transaction
from django.utils import timezone

from accounts.decorators import admin_required
from notifications.emails import send_application_status_update


@admin_required
def admin_applications_list_view(request):
    """
    Filterable list of all adoption applications for the admin dashboard.
    Supports filtering by status, pet name, and date range.
    """
    queryset = (
        AdoptionApplication.objects
        .select_related('pet', 'applicant')
        .order_by('-submitted_at')
    )

    status_filter = request.GET.get('status', '')
    pet_filter = request.GET.get('pet_name', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if pet_filter:
        queryset = queryset.filter(pet__name__icontains=pet_filter)
    if date_from:
        queryset = queryset.filter(submitted_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(submitted_at__date__lte=date_to)

    pending_count = AdoptionApplication.objects.filter(status='pending').count()

    return render(request, 'dashboard/applications_list.html', {
        'applications': queryset,
        'pending_count': pending_count,
        'status_filter': status_filter,
        'pet_filter': pet_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': AdoptionApplication.STATUS_CHOICES,
    })


@admin_required
def admin_application_review_view(request, pk):
    """
    Detailed review page for a single adoption application.
    Supports three actions:
      under_review — moves to Under Review (no email sent)
      approve      — approves, marks pet as adopted, rejects competing apps, sends email
      reject       — rejects with mandatory admin remarks, sends email
    """
    from pets.models import Pet

    application = get_object_or_404(
        AdoptionApplication.objects.select_related('pet', 'applicant'),
        pk=pk,
    )
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'under_review':
            application.status = 'under_review'
            application.reviewed_at = timezone.now()
            application.save()
            messages.success(request, 'Application marked as Under Review.')
            return redirect('dashboard:application_review', pk=pk)

        elif action == 'approve':
            with transaction.atomic():
                application.status = 'approved'
                application.reviewed_at = timezone.now()
                application.admin_remarks = request.POST.get('admin_remarks', '')
                application.save()
                application.pet.status = 'adopted'
                application.pet.save()
                # Reject all other open applications for this pet
                AdoptionApplication.objects.filter(
                    pet=application.pet,
                    status__in=['pending', 'under_review'],
                ).exclude(pk=application.pk).update(status='rejected')
            send_application_status_update(application)
            messages.success(
                request,
                f'Application approved. {application.pet.name} is now marked as Adopted.',
            )
            return redirect('dashboard:applications_list')

        elif action == 'reject':
            remarks = request.POST.get('admin_remarks', '').strip()
            if not remarks:
                error = 'Please provide a rejection reason before rejecting.'
            else:
                application.status = 'rejected'
                application.reviewed_at = timezone.now()
                application.admin_remarks = remarks
                application.save()
                send_application_status_update(application)
                messages.success(request, 'Application rejected.')
                return redirect('dashboard:applications_list')

    pending_count = AdoptionApplication.objects.filter(status='pending').count()

    return render(request, 'dashboard/application_review.html', {
        'application': application,
        'pending_count': pending_count,
        'error': error,
    })
