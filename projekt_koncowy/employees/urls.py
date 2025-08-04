from django.urls import path
from .views import employee_list, add_employee, edit_employee, delete_employee, assign_employees_view
from . import views

urlpatterns = [
    path('', employee_list, name='employee_list'),
    path('add/', add_employee, name='add_employee'),
    path('assign/', assign_employees_view, name='assign_employees'),
    path('edit/<int:employee_id>/', edit_employee, name='edit_employee'),
    path('delete/<int:employee_id>/', delete_employee, name='delete_employee'),
    path('assignment/add/', views.add_assignment, name='add_assignment'),
]
