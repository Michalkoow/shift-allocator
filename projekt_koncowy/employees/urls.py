from django.urls import path
from .views import employee_list, add_employee

urlpatterns = [
    path('', employee_list, name='employee_list'),
    path('add/', add_employee, name='add_employee'),
]
