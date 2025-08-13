# importy
import pytest
from datetime import date, time
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from employees.models import Employee, Department, Shift, Assignment


# ---------- fikstury ----------
@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user(db):
    return User.objects.create_user(username="tester", password="pass12345")

@pytest.fixture
def logged_client(client, user):
    client.login(username="tester", password="pass12345")
    return client

@pytest.fixture
def dept_sales(db):
    return Department.objects.create(name="Sales", capacity=5)

@pytest.fixture
def dept_hr(db):
    return Department.objects.create(name="HR", capacity=5)

@pytest.fixture
def shift_morning(db):
    return Shift.objects.create(name="Morning", start_time=time(8, 0), end_time=time(16, 0))

@pytest.fixture
def employee_jan(db, dept_sales):
    emp = Employee.objects.create(
        first_name="Jan",
        last_name="Kowalski",
        status="available",
        hire_date=date(2024, 1, 1),
    )
    emp.department.add(dept_sales)
    return emp


# ---------- employee_list (publiczny) ----------
@pytest.mark.django_db
def test_employee_list_returns_200_for_anon(client):
    url = reverse('employee_list')
    resp = client.get(url)
    assert resp.status_code == 200
    assert b'Employee List' in resp.content

@pytest.mark.django_db
def test_employee_list_search_and_sort_works(client, employee_jan):
    url = reverse('employee_list')
    resp = client.get(url, {"q": "Kow", "sort": "desc"})
    assert resp.status_code == 200
    assert b'Kowalski' in resp.content


# ---------- add_employee (chroniony) ----------
@pytest.mark.django_db
def test_add_employee_get_redirects_when_anon(client):
    url = reverse('add_employee')
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_add_employee_get_returns_200_when_logged(logged_client):
    url = reverse('add_employee')
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'<form' in resp.content

@pytest.mark.django_db
def test_add_employee_post_creates_when_logged(logged_client):
    url = reverse('add_employee')
    data = {
        'first_name': 'Jan',
        'last_name': 'Kowalski',
        'status': 'available',
        'hire_date': '2024-01-01'
    }
    resp = logged_client.post(url, data)
    assert resp.status_code == 302  # redirect po sukcesie
    assert Employee.objects.filter(first_name='Jan', last_name='Kowalski').exists()

@pytest.mark.django_db
def test_add_employee_post_invalid_stays_on_form_when_logged(logged_client):
    url = reverse('add_employee')
    data = {
        'first_name': 'BezNazwiska',
        # brak last_name
        'status': 'available',
        'hire_date': '2024-01-01'
    }
    resp = logged_client.post(url, data)
    assert resp.status_code == 200  # zostaje na formularzu
    assert Employee.objects.filter(first_name='BezNazwiska').count() == 0


# ---------- edit_employee (chroniony) ----------
@pytest.mark.django_db
def test_edit_employee_get_redirects_when_anon(client, employee_jan):
    url = reverse('edit_employee', args=[employee_jan.id])
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_edit_employee_get_returns_200_when_logged(logged_client, employee_jan):
    url = reverse('edit_employee', args=[employee_jan.id])
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'Edit Employee' in resp.content

@pytest.mark.django_db
def test_edit_employee_post_updates_when_logged(logged_client, employee_jan):
    url = reverse('edit_employee', args=[employee_jan.id])
    data = {
        'first_name': 'Jan',
        'last_name': 'Zmieniony',
        'status': 'holiday',
        'hire_date': '2024-01-01',
    }
    resp = logged_client.post(url, data)
    assert resp.status_code == 302
    employee_jan.refresh_from_db()
    assert employee_jan.last_name == 'Zmieniony'
    assert employee_jan.status == 'holiday'


# ---------- delete_employee (chroniony) ----------
@pytest.mark.django_db
def test_delete_employee_get_redirects_when_anon(client, employee_jan):
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_delete_employee_get_confirmation_when_logged(logged_client, employee_jan):
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'Confirm Delete' in resp.content

@pytest.mark.django_db
def test_delete_employee_post_removes_when_logged(logged_client, employee_jan):
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = logged_client.post(url)
    assert resp.status_code == 302
    assert not Employee.objects.filter(id=employee_jan.id).exists()


# ---------- assignment_list (chroniony) ----------
@pytest.mark.django_db
def test_assignment_list_redirects_when_anon(client):
    url = reverse('assignment_list')
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_assignment_list_returns_200_when_logged(logged_client):
    url = reverse('assignment_list')
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'Assignment List' in resp.content

@pytest.mark.django_db
def test_assignment_list_filters_by_date_when_logged(logged_client, employee_jan, dept_sales, shift_morning):
    Assignment.objects.create(employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 1))
    Assignment.objects.create(employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 2))
    url = reverse('assignment_list')
    resp = logged_client.get(url, {"date": "2025-01-02"})
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "2025-01-02" in html
    assert "2025-01-01" not in html


# ---------- add_assignment (chroniony) ----------
@pytest.mark.django_db
def test_add_assignment_get_redirects_when_anon(client):
    url = reverse('add_assignment')
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_add_assignment_post_creates_when_logged(logged_client, employee_jan, dept_sales, shift_morning):
    url = reverse('add_assignment')
    resp = logged_client.post(url, {
        "employee": employee_jan.id,
        "department": dept_sales.id,
        "shift": shift_morning.id,
        "date": "2025-01-03",
    })
    assert resp.status_code in (302, 303)
    assert Assignment.objects.filter(
        employee=employee_jan,
        department=dept_sales,
        shift=shift_morning,
        date=date(2025, 1, 3),
    ).exists()


# ---------- assign_employees (chroniony) ----------
@pytest.mark.django_db
def test_assign_employees_get_redirects_or_renders_form(client):
    """
    Jeśli masz @login_required -> spodziewaj się 302 do /login/.
    Jeśli GET ma tylko pokazać stronę z przyciskiem (bez login_required) -> 200.
    """
    url = reverse("assign_employees")
    resp = client.get(url)
    assert resp.status_code in (200, 302)

@pytest.mark.django_db
def test_assign_employees_post_assigns_when_logged(logged_client, dept_sales):
    # dwóch dostępnych bez działu
    e1 = Employee.objects.create(first_name="A", last_name="A", status="available", hire_date=date(2024, 1, 1))
    e2 = Employee.objects.create(first_name="B", last_name="B", status="available", hire_date=date(2024, 1, 2))

    url = reverse("assign_employees")
    resp = logged_client.post(url)
    assert resp.status_code == 200  # render wyników przydziału

    e1.refresh_from_db()
    e2.refresh_from_db()
    assert e1.department.exists()
    assert e2.department.exists()
