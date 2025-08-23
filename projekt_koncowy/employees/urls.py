from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add_employee'),
    path('edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),

    path('assign/', views.assign_employees_view, name='assign_employees'),
    path('assignment/add/', views.add_assignment, name='add_assignment'),
    path('assignments/', views.assignment_list, name='assignment_list'),

    path('login/',  auth_views.LoginView.as_view(template_name='employees/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),

]
