from django.urls import path

from . import views

app_name = 'surrenders'

urlpatterns = [
    # Public routes
    path('', views.surrender_form_view, name='form'),
    path('success/', views.surrender_success_view, name='success'),

    # Admin routes (mounted under /dashboard/surrenders/ via dashboard/urls.py)
    path('manage/', views.admin_surrender_list_view, name='admin_list'),
    path('manage/<int:pk>/', views.admin_surrender_detail_view, name='admin_detail'),
]
