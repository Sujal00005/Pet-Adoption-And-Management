from django.db import models


class SurrenderRequest(models.Model):
    """
    A request submitted by a member of the public to hand a pet over to the shelter.

    No user account is required — the submitter's contact details are
    captured directly on the form.  The admin reviews each request and
    can attach internal notes before marking it as 'Reviewed'.
    """

    STATUS_CHOICES = [
        ('new',      'New'),
        ('reviewed', 'Reviewed'),
    ]

    # Who is surrendering the pet
    submitter_name  = models.CharField(max_length=200)
    submitter_phone = models.CharField(max_length=20)
    submitter_email = models.EmailField()

    # The pet being surrendered
    pet_name        = models.CharField(max_length=100)
    species         = models.CharField(max_length=50)
    breed           = models.CharField(max_length=100, blank=True)
    approximate_age = models.CharField(max_length=50, blank=True)
    gender          = models.CharField(max_length=10, blank=True)
    is_vaccinated   = models.BooleanField(default=False)
    health_notes    = models.TextField(blank=True)
    reason          = models.TextField()

    # Admin review tracking
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Surrender: {self.pet_name} by {self.submitter_name}"
