import pytest
from django.urls import reverse
from django.test import Client
from employees.models import Employee
from datetime import date

# Test widoku listy pracowników
@pytest.mark.django_db
def test_employee_list_view_returns_200():
    client = Client()
    url = reverse('employee_list')
    response = client.get(url)
    assert response.status_code == 200
    assert b'Employee List' in response.content

# Test GET - formularz dodawania pracownika
@pytest.mark.django_db
def test_add_employee_view_get():
    client = Client()
    url = reverse('add_employee')
    response = client.get(url)
    assert response.status_code == 200
    assert b'<form' in response.content  # Czy formularz jest na stronie?

# Test POST - dodawanie nowego pracownika
@pytest.mark.django_db
def test_add_employee_view_post():
    client = Client()
    url = reverse('add_employee')
    data = {
        'first_name': 'Jan',
        'last_name': 'Kowalski',
        'status': 'available',
        'hire_date': '2024-01-01'
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Oczekujemy przekierowania
    assert Employee.objects.filter(first_name='Jan', last_name='Kowalski').exists()
