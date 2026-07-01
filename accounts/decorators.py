"""
Role-based access control decorators for function-based views.

Usage:
    @admin_required
    def my_admin_view(request):
        ...

    @adopter_required
    def my_adopter_view(request):
        ...
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def admin_required(view_func):
    """
    Decorator that restricts a view to authenticated users with role == 'admin'.
    - Unauthenticated users are redirected to the login page.
    - Authenticated non-admins get a 403 Forbidden response.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        try:
            is_admin = request.user.profile.role == 'admin'
        except AttributeError:
            is_admin = False
        if not is_admin:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def adopter_required(view_func):
    """
    Decorator that restricts a view to any authenticated user.
    Unauthenticated users are redirected to the login page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper
