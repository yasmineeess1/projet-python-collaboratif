from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_tasks, name='list'),
    path('delete/<int:task_id>/', views.delete_task, name='delete'),
    path('edit/<int:task_id>/', views.edit_task, name='edit'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle'),

    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', accounts_views.register, name='register'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('history/', views.task_history, name='task_history'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),

]
