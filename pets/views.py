"""
Public pet browsing views and (later) admin pet management.

Task 5.2 — pet_list_view and pet_detail_view for the public-facing portal.
"""

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from adoptions.models import AdoptionApplication

from .forms import BREEDS_BY_SPECIES, PetFilterForm
from .models import Pet


def pet_list_view(request):
    """
    Public browsing page — shows available pets with optional filters and pagination.

    No authentication required. Filters are submitted via GET so bookmarking
    and pagination links preserve the active search criteria.
    """
    queryset = (
        Pet.objects.filter(status='available')
        .prefetch_related('photos')
    )

    form = PetFilterForm(request.GET)
    filters_active = False

    if form.is_valid():
        data = form.cleaned_data

        if data.get('q'):
            filters_active = True
            term = data['q']
            queryset = queryset.filter(
                Q(name__icontains=term)
                | Q(breed__icontains=term)
                | Q(description__icontains=term)
            )

        if data.get('species'):
            filters_active = True
            queryset = queryset.filter(species=data['species'])

        if data.get('breed'):
            filters_active = True
            queryset = queryset.filter(breed__icontains=data['breed'])

        if data.get('gender'):
            filters_active = True
            queryset = queryset.filter(gender=data['gender'])

        if data.get('size'):
            filters_active = True
            queryset = queryset.filter(size=data['size'])

        if data.get('location'):
            filters_active = True
            queryset = queryset.filter(location__icontains=data['location'])

        if data.get('min_age_years') is not None:
            filters_active = True
            queryset = queryset.filter(age_years__gte=data['min_age_years'])

        if data.get('max_age_years') is not None:
            filters_active = True
            queryset = queryset.filter(age_years__lte=data['max_age_years'])

    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Preserve filter params in pagination links (drop the page number).
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()

    total_available = Pet.objects.filter(status='available').count()

    return render(request, 'pets/browse.html', {
        'form': form,
        'page_obj': page_obj,
        'pets': page_obj.object_list,
        'query_string': query_string,
        'filters_active': filters_active,
        'total_available': total_available,
        'breeds_by_species': BREEDS_BY_SPECIES,
    })


def pet_detail_view(request, pk):
    """
    Full pet profile page — public, no auth required.

    Shows all pet details and photos. Authenticated adopters see an Apply button
    or their existing application status; visitors see a login prompt.
    """
    pet = get_object_or_404(
        Pet.objects.prefetch_related('photos'),
        pk=pk,
    )
    photos = list(pet.photos.all())

    existing_application = None
    if request.user.is_authenticated:
        existing_application = AdoptionApplication.objects.filter(
            pet=pet,
            applicant=request.user,
        ).first()

    is_adopter = (
        request.user.is_authenticated
        and getattr(getattr(request.user, 'profile', None), 'role', None) == 'adopter'
    )

    return render(request, 'pets/detail.html', {
        'pet': pet,
        'photos': photos,
        'existing_application': existing_application,
        'is_adopter': is_adopter,
        'show_gallery_controls': len(photos) > 1,
    })


# ---------------------------------------------------------------------------
# Admin pet management views — added in Task 8.2
# ---------------------------------------------------------------------------

from django import forms as django_forms
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect

from accounts.decorators import admin_required
from adoptions.models import AdoptionApplication

from .forms import PetPhotoForm
from .models import PetPhoto


class PetForm(django_forms.ModelForm):
    """ModelForm for creating and editing Pet listings."""

    class Meta:
        model = Pet
        fields = [
            'name', 'species', 'breed', 'age_years', 'age_months',
            'gender', 'size', 'color_markings', 'description',
            'temperament', 'good_with_kids', 'good_with_pets',
            'is_vaccinated', 'is_neutered', 'medical_notes',
            'location', 'status',
        ]


def _mark_pet_adopted(pet):
    """Mark a pet as adopted and reject all its pending/under-review applications."""
    pet.status = 'adopted'
    pet.save()
    AdoptionApplication.objects.filter(
        pet=pet, status__in=['pending', 'under_review']
    ).update(status='rejected')


@admin_required
def admin_pet_list_view(request):
    """Dashboard list of all pets with edit/delete actions."""
    pets = Pet.objects.prefetch_related('photos').order_by('-listed_at')
    pending_count = AdoptionApplication.objects.filter(status='pending').count()
    return render(request, 'dashboard/pets_list.html', {
        'pets': pets,
        'pending_count': pending_count,
    })


@admin_required
def admin_pet_add_view(request):
    """Form to create a new pet listing with an optional primary photo."""
    pet_form = PetForm()
    photo_form = PetPhotoForm()

    if request.method == 'POST':
        pet_form = PetForm(request.POST)
        photo_form = PetPhotoForm(request.POST, request.FILES)
        if pet_form.is_valid() and photo_form.is_valid():
            pet = pet_form.save(commit=False)
            pet.added_by = request.user
            pet.save()
            image = photo_form.cleaned_data.get('image')
            if image:
                PetPhoto.objects.create(
                    pet=pet,
                    image=image,
                    caption=photo_form.cleaned_data.get('caption', ''),
                    is_primary=True,
                )
            messages.success(request, f'{pet.name} has been added.')
            return redirect('dashboard:pets_list')

    return render(request, 'dashboard/pet_form.html', {
        'pet_form': pet_form,
        'photo_form': photo_form,
        'action': 'Add',
        'pending_count': AdoptionApplication.objects.filter(status='pending').count(),
    })


@admin_required
def admin_pet_edit_view(request, pk):
    """Form to edit an existing pet listing; optionally upload a new photo."""
    pet = get_object_or_404(Pet, pk=pk)
    pet_form = PetForm(instance=pet)
    photo_form = PetPhotoForm()

    if request.method == 'POST':
        pet_form = PetForm(request.POST, instance=pet)
        photo_form = PetPhotoForm(request.POST, request.FILES)
        if pet_form.is_valid() and photo_form.is_valid():
            updated_pet = pet_form.save()
            # If the status was explicitly set to 'adopted', close all open apps.
            if pet_form.cleaned_data.get('status') == 'adopted':
                _mark_pet_adopted(updated_pet)
            image = photo_form.cleaned_data.get('image')
            if image:
                PetPhoto.objects.create(
                    pet=updated_pet,
                    image=image,
                    caption=photo_form.cleaned_data.get('caption', ''),
                    is_primary=photo_form.cleaned_data.get('is_primary', False),
                )
            messages.success(request, f'{updated_pet.name} has been updated.')
            return redirect('dashboard:pets_list')

    return render(request, 'dashboard/pet_form.html', {
        'pet_form': pet_form,
        'photo_form': photo_form,
        'pet': pet,
        'action': 'Edit',
        'pending_count': AdoptionApplication.objects.filter(status='pending').count(),
    })


@admin_required
def admin_pet_delete_view(request, pk):
    """Confirm and delete a pet listing."""
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == 'POST':
        name = pet.name
        pet.delete()
        messages.success(request, f'{name} has been deleted.')
        return redirect('dashboard:pets_list')
    return render(request, 'dashboard/pet_confirm_delete.html', {
        'pet': pet,
        'pending_count': AdoptionApplication.objects.filter(status='pending').count(),
    })
