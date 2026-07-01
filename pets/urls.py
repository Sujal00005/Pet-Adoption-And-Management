from django.urls import path

from . import views

app_name = 'pets'

urlpatterns = [
    # Public routes
    path('', views.pet_list_view, name='browse'),
    path('<int:pk>/', views.pet_detail_view, name='detail'),

    # Admin pet management routes (mounted under /dashboard/pets/ via dashboard/urls.py)
    path('manage/', views.admin_pet_list_view, name='admin_list'),
    path('manage/add/', views.admin_pet_add_view, name='admin_add'),
    path('manage/<int:pk>/edit/', views.admin_pet_edit_view, name='admin_edit'),
    path('manage/<int:pk>/delete/', views.admin_pet_delete_view, name='admin_delete'),
]
