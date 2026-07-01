"""
Email notification helpers for the portal.

Failures are logged but never block the user-facing flow — the underlying
database record is still saved even if SMTP is unavailable.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_application_confirmation(application):
    """Notify an adopter that their adoption application was received."""
    pet_name = application.pet.name
    applicant_email = application.applicant.email
    submitted = application.submitted_at.strftime('%B %d, %Y at %I:%M %p')

    subject = f'Application Received — {pet_name}'
    message = (
        f'Hello {application.full_name},\n\n'
        f'Thank you for applying to adopt {pet_name}. '
        f'We received your application on {submitted}.\n\n'
        f'Our team will review your application and update you on its status. '
        f'You can track progress anytime from the My Applications page:\n'
        f'{settings.LOGIN_REDIRECT_URL.rstrip("/")}/adoptions/my-applications/\n\n'
        f'Warm regards,\n'
        f'Paws & Hearts Shelter'
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[applicant_email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            'Failed to send application confirmation email for application %s',
            application.pk,
        )


def send_application_status_update(application):
    """Notify an adopter when their application is approved or rejected."""
    if application.status not in ('approved', 'rejected'):
        return

    pet_name = application.pet.name
    status_label = application.get_status_display()
    subject = f'Your Application for {pet_name} has been {status_label}'

    message = (
        f'Hello {application.full_name},\n\n'
        f'Your adoption application for {pet_name} has been {status_label.lower()}.\n'
    )
    if application.admin_remarks:
        message += f'\nRemarks from our team:\n{application.admin_remarks}\n'
    message += (
        f'\nView your application details here:\n'
        f'{settings.LOGIN_REDIRECT_URL.rstrip("/")}/adoptions/{application.pk}/\n\n'
        f'Warm regards,\n'
        f'Paws & Hearts Shelter'
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.applicant.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            'Failed to send status update email for application %s',
            application.pk,
        )


def send_surrender_notification_to_admin(surrender):
    """Alert the shelter admin about a new surrender request."""
    subject = f'New Surrender Request — {surrender.pet_name}'
    message = (
        f'A new surrender request has been submitted.\n\n'
        f'Submitter: {surrender.submitter_name}\n'
        f'Phone: {surrender.submitter_phone}\n'
        f'Email: {surrender.submitter_email}\n\n'
        f'Pet: {surrender.pet_name} ({surrender.species})\n'
        f'Breed: {surrender.breed or "Not specified"}\n'
        f'Approximate age: {surrender.approximate_age or "Not specified"}\n'
        f'Gender: {surrender.gender or "Not specified"}\n'
        f'Vaccinated: {"Yes" if surrender.is_vaccinated else "No"}\n'
        f'Health notes: {surrender.health_notes or "None"}\n\n'
        f'Reason for surrender:\n{surrender.reason}\n\n'
        f'Review this request in the admin dashboard.'
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            'Failed to send surrender notification for request %s',
            surrender.pk,
        )
