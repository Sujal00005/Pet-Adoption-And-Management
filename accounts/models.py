from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extends Django's built-in User with a role (admin or adopter)
    and a phone number.  One profile is created automatically for
    every new User via the post_save signal below.
    """

    ROLE_CHOICES = [
        ('admin',   'Admin'),
        ('adopter', 'Adopter'),
    ]

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default='adopter')
    phone      = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Fall back to username when the user hasn't set a full name yet
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile whenever a new User is saved."""
    if created:
        UserProfile.objects.create(user=instance)
