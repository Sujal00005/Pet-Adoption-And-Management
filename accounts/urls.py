from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/',       views.register_view,       name='register'),
    path('admin-register/', views.admin_register_view, name='admin_register'),
    path('login/',          views.login_view,          name='login'),
    path('logout/',         views.logout_view,         name='logout'),
]
