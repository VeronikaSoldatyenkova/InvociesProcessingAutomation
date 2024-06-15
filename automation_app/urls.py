# automation_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('change_password/', views.change_password_view, name='change_password'),
    path('add_automation/', views.add_automation, name='add_automation'),
    path('delete_automation/<int:automation_id>/', views.delete_automation, name='delete_automation'),
    path('run_automation/<int:automation_id>/', views.run_automation, name='run_automation'),
]
