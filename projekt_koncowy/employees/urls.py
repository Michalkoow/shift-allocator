from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import DepartmentListView, DepartmentCreateView, DepartmentDeleteView, DepartmentUpdateView

urlpatterns = [
    # Pracownicy
    path('', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add_employee'),
    path('edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),

    # Przydziały
    path('assign/', views.assign_employees_view, name='assign_employees'),
    path('assignment/add/', views.add_assignment, name='add_assignment'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),

    # Działy
    path("departments/", DepartmentListView.as_view(), name="department_list"),
    path("departments/add/", DepartmentCreateView.as_view(), name="department_add"),
    path("departments/<int:pk>/edit/", DepartmentUpdateView.as_view(), name="department_edit"),  # ⬅️ nowy
    path("departments/<int:pk>/delete/", DepartmentDeleteView.as_view(), name="department_delete"),


    # Auth
    path('login/',  auth_views.LoginView.as_view(template_name='employees/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='employee_list'), name='logout'),
    path('register/', views.register, name='register'),
]