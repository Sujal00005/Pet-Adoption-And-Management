from django.db import models
from django.contrib.auth.models import User


def pet_photo_upload_path(instance, filename):
    """Save uploaded pet photos to media/pets/<pet_id>/<filename>."""
    return f"pets/{instance.pet.pk}/{filename}"


class Pet(models.Model):
    """
    Represents an animal listed on the portal.

    A pet progresses through these statuses:
      available → pending → adopted  (normal adoption flow)
      available → unavailable        (temporarily off-market)

    The age is stored as two separate integer fields (years + months)
    so we can display it naturally, e.g. "1 yr, 6 mo".
    """

    SPECIES_CHOICES = [
        ('dog',    'Dog'),
        ('cat',    'Cat'),
        ('rabbit', 'Rabbit'),
        ('bird',   'Bird'),
        ('other',  'Other'),
    ]
    GENDER_CHOICES = [
        ('male',    'Male'),
        ('female',  'Female'),
        ('unknown', 'Unknown'),
    ]
    SIZE_CHOICES = [
        ('small',  'Small'),
        ('medium', 'Medium'),
        ('large',  'Large'),
        ('xlarge', 'Extra Large'),
    ]
    STATUS_CHOICES = [
        ('available',   'Available'),
        ('adopted',     'Adopted'),
        ('pending',     'Pending'),
        ('unavailable', 'Unavailable'),
    ]

    name           = models.CharField(max_length=100)
    species        = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed          = models.CharField(max_length=100, blank=True)
    age_years      = models.PositiveSmallIntegerField(default=0)
    age_months     = models.PositiveSmallIntegerField(default=0)
    gender         = models.CharField(max_length=10, choices=GENDER_CHOICES)
    size           = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color_markings = models.CharField(max_length=200, blank=True)
    description    = models.TextField()
    temperament    = models.TextField(blank=True)
    good_with_kids = models.BooleanField(default=False)
    good_with_pets = models.BooleanField(default=False)

    # Health info
    is_vaccinated  = models.BooleanField(default=False)
    is_neutered    = models.BooleanField(default=False)
    medical_notes  = models.TextField(blank=True)

    # Location — free-text city name typed by admin
    location       = models.CharField(max_length=150)

    status         = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    listed_at      = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    added_by       = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_pets',
    )

    class Meta:
        ordering = ['-listed_at']

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"

    @property
    def primary_photo(self):
        """Return the first (primary) photo, or None if no photos uploaded yet."""
        return self.photos.filter(is_primary=True).first() or self.photos.first()

    @property
    def age_display(self):
        """
        Human-readable age, e.g. '2 yrs, 3 mo' or '6 mo' or 'Unknown'.
        Keeps the UI consistent without extra template logic.
        """
        parts = []
        if self.age_years:
            label = 'yr' if self.age_years == 1 else 'yrs'
            parts.append(f"{self.age_years} {label}")
        if self.age_months:
            parts.append(f"{self.age_months} mo")
        return ', '.join(parts) if parts else 'Unknown'


class PetPhoto(models.Model):
    """
    One or more photos for a Pet.
    The primary photo is shown in listing cards; all photos appear
    in the gallery on the pet profile page.
    """

    pet         = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='photos')
    image       = models.ImageField(upload_to=pet_photo_upload_path)
    caption     = models.CharField(max_length=200, blank=True)
    is_primary  = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Primary photo sorts first; within each group, oldest first
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        label = 'primary' if self.is_primary else 'gallery'
        return f"Photo of {self.pet.name} ({label})"
