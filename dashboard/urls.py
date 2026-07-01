"""
Dashboard URL configuration.

All routes here require admin access (enforced per-view with @admin_required).
We wire views directly instead of using include() to keep namespacing simple
and avoid any nested-namespace conflicts.
"""

from django.urls import path

from . import views
from adoptions import views as adoption_views
from pets import views as pet_views
from surrenders import views as surrender_views

app_name = 'dashboard'

urlpatterns = [
    # Overview
    path('', views.dashboard_home_view, name='home'),

    # Pet management
    path('pets/', pet_views.admin_pet_list_view, name='pets_list'),
    path('pets/add/', pet_views.admin_pet_add_view, name='pet_add'),
    path('pets/<int:pk>/edit/', pet_views.admin_pet_edit_view, name='pet_edit'),
    path('pets/<int:pk>/delete/', pet_views.admin_pet_delete_view, name='pet_delete'),

    # Application management
    path('applications/', adoption_views.admin_applications_list_view, name='applications_list'),
    path('applications/<int:pk>/review/', adoption_views.admin_application_review_view, name='application_review'),

    # User (adopter) management
    path('users/', views.user_list_view, name='users_list'),
    path('users/<int:pk>/', views.user_detail_view, name='user_detail'),

    # Surrender management
    path('surrenders/', surrender_views.admin_surrender_list_view, name='surrenders_list'),
    path('surrenders/<int:pk>/', surrender_views.admin_surrender_detail_view, name='surrender_detail'),
]
