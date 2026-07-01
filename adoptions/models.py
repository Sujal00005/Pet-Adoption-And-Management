from django.db import models
from django.contrib.auth.models import User
from pets.models import Pet


class AdoptionApplication(models.Model):
    """
    A formal adoption request submitted by an Adopter for a specific Pet.

    Personal details (name, phone, address) are stored directly on the
    application rather than looked up live from the user's profile.
    This means that if an adopter later changes their profile, historical
    applications still show the information that was correct at submission.

    The unique_together constraint enforces one application per adopter
    per pet at the database level — the form also validates this, but
    this is the safety net.
    """

    HOUSING_CHOICES = [
        ('house',     'House'),
        ('apartment', 'Apartment'),
        ('other',     'Other'),
    ]
    TENANCY_CHOICES = [
        ('owns',  'Owns'),
        ('rents', 'Rents'),
    ]
    STATUS_CHOICES = [
        ('pending',      'Pending'),
        ('under_review', 'Under Review'),
        ('approved',     'Approved'),
        ('rejected',     'Rejected'),
    ]

    # Who is applying for which pet
    pet       = models.ForeignKey(Pet,  on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')

    # Personal details — captured at submission time so changes to the profile don't affect existing apps
    full_name = models.CharField(max_length=200)
    phone     = models.CharField(max_length=20)
    address   = models.TextField()

    # Housing situation
    housing_type     = models.CharField(max_length=15, choices=HOUSING_CHOICES)
    owns_or_rents    = models.CharField(max_length=10, choices=TENANCY_CHOICES)
    landlord_contact = models.CharField(max_length=200, blank=True)

    # Household info
    household_members   = models.PositiveSmallIntegerField(default=1)
    has_other_pets      = models.BooleanField(default=False)
    other_pets_desc     = models.CharField(max_length=300, blank=True)
    prev_pet_experience = models.TextField(blank=True)

    # Adoption intent
    reason_for_adoption  = models.TextField()
    agrees_to_home_visit = models.BooleanField(default=False)

    # Status and admin feedback
    status        = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    admin_remarks = models.TextField(blank=True)
    submitted_at  = models.DateTimeField(auto_now_add=True)
    reviewed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        # Prevent the same adopter from submitting more than one application per pet
        unique_together = [('pet', 'applicant')]

    def __str__(self):
        return f"{self.full_name} → {self.pet.name} [{self.get_status_display()}]"
