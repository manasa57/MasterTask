from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add-task/', views.add_task_view, name='add_task'),
    path('edit-task/<int:task_id>/', views.edit_task_view, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task_view, name='delete_task'),
    path('update-status/<int:task_id>/', views.update_status, name='update_status'),
    path('profile/', views.profile_settings_view, name='profile'),
    path('reports/', views.reports_view, name='reports'),

]
