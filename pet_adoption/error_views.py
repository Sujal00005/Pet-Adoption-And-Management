"""
Custom HTTP error view functions.

Django calls these instead of its built-in error pages when the handlers are
registered in urls.py. Each function just renders the matching template; Django
passes the request and, for 403/404, some extra context.
"""

from django.shortcuts import render


def handler_403(request, exception=None):
    """Render the 403 Forbidden page."""
    return render(request, '403.html', status=403)


def handler_404(request, exception=None):
    """Render the 404 Not Found page."""
    return render(request, '404.html', status=404)


def handler_500(request):
    """Render the 500 Internal Server Error page."""
    return render(request, '500.html', status=500)
