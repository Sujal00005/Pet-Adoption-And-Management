from django.urls import path

from . import views

app_name = 'adoptions'

urlpatterns = [
    # Adopter-facing routes
    path('apply/<int:pet_pk>/', views.apply_view, name='apply'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('<int:pk>/', views.application_detail_view, name='detail'),

    # Admin routes (mounted under /dashboard/applications/ via dashboard/urls.py)
    path('manage/', views.admin_applications_list_view, name='admin_list'),
    path('manage/<int:pk>/review/', views.admin_application_review_view, name='admin_review'),
]
