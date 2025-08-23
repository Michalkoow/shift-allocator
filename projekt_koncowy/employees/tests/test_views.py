# ================== TESTY PROJEKTU SHIFT ALLOCATOR ==================
# Każda sekcja odpowiada widokowi. Testuję różne scenariusze:
# - dostęp dla zalogowanych / niezalogowanych
# - poprawne działanie formularzy
# - poprawne filtrowanie / sortowanie / przydzielanie
# ====================================================================

import pytest
from datetime import date, time
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from employees.models import Employee, Department, Shift, Assignment


# ---------- FIKSTURY (przygotowanie danych do testów) ----------
@pytest.fixture
def client():
    return Client()  # zwykły klient (niezalogowany)

@pytest.fixture
def user(db):
    # tworzymy użytkownika testowego
    return User.objects.create_user(username="tester", password="pass12345")

@pytest.fixture
def logged_client(client, user):
    # logowanie klienta do testów chronionych widoków
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
    # przykładowy pracownik do testów
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
    # ✅ Czy lista pracowników działa dla niezalogowanego
    url = reverse('employee_list')
    resp = client.get(url)
    assert resp.status_code == 200
    assert b'Employee List' in resp.content

@pytest.mark.django_db
def test_employee_list_search_and_sort_works(client, employee_jan):
    # ✅ Czy działa wyszukiwanie i sortowanie po nazwisku
    url = reverse('employee_list')
    resp = client.get(url, {"q": "Kow", "sort": "desc"})
    assert resp.status_code == 200
    assert b'Kowalski' in resp.content


# ---------- add_employee (chroniony) ----------
@pytest.mark.django_db
def test_add_employee_get_redirects_when_anon(client):
    # ❌ Niezalogowany nie ma dostępu do dodawania
    url = reverse('add_employee')
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_add_employee_get_returns_200_when_logged(logged_client):
    # ✅ Zalogowany widzi formularz dodawania
    url = reverse('add_employee')
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'<form' in resp.content

@pytest.mark.django_db
def test_add_employee_post_creates_when_logged(logged_client):
    # ✅ Dodanie pracownika działa (redirect po sukcesie)
    url = reverse('add_employee')
    data = {
        'first_name': 'Jan',
        'last_name': 'Kowalski',
        'status': 'available',
        'hire_date': '2024-01-01'
    }
    resp = logged_client.post(url, data)
    assert resp.status_code == 302
    assert Employee.objects.filter(first_name='Jan', last_name='Kowalski').exists()

@pytest.mark.django_db
def test_add_employee_post_invalid_stays_on_form_when_logged(logged_client):
    # ❌ Formularz z błędem zostaje na stronie (brak last_name)
    url = reverse('add_employee')
    data = {
        'first_name': 'BezNazwiska',
        'status': 'available',
        'hire_date': '2024-01-01'
    }
    resp = logged_client.post(url, data)
    assert resp.status_code == 200
    assert Employee.objects.filter(first_name='BezNazwiska').count() == 0


# ---------- edit_employee (chroniony) ----------
@pytest.mark.django_db
def test_edit_employee_get_redirects_when_anon(client, employee_jan):
    # ❌ Niezalogowany nie może edytować
    url = reverse('edit_employee', args=[employee_jan.id])
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_edit_employee_get_returns_200_when_logged(logged_client, employee_jan):
    # ✅ Zalogowany widzi formularz edycji
    url = reverse('edit_employee', args=[employee_jan.id])
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'Edit Employee' in resp.content

@pytest.mark.django_db
def test_edit_employee_post_updates_when_logged(logged_client, employee_jan):
    # ✅ Edycja działa, zmienia nazwisko i status
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
    # ❌ Niezalogowany nie ma dostępu do usuwania
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_delete_employee_get_confirmation_when_logged(logged_client, employee_jan):
    # ✅ Zalogowany widzi stronę potwierdzenia usunięcia
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'Confirm Delete' in resp.content

@pytest.mark.django_db
def test_delete_employee_post_removes_when_logged(logged_client, employee_jan):
    # ✅ Po zatwierdzeniu pracownik jest usuwany
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = logged_client.post(url)
    assert resp.status_code == 302
    assert not Employee.objects.filter(id=employee_jan.id).exists()


# ---------- assignment_list (chroniony) ----------
@pytest.mark.django_db
def test_assignment_list_redirects_when_anon(client):
    # ❌ Niezalogowany nie widzi listy przydziałów
    url = reverse('assignment_list')
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_assignment_list_returns_200_when_logged(logged_client):
    # ✅ Zalogowany widzi listę przydziałów
    url = reverse('assignment_list')
    resp = logged_client.get(url)
    assert resp.status_code == 200
    assert b'Assignment List' in resp.content

@pytest.mark.django_db
def test_assignment_list_filters_by_date_when_logged(logged_client, employee_jan, dept_sales, shift_morning):
    # ✅ Filtrowanie działa (po dacie)
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
    # ❌ Niezalogowany nie może wejść na dodawanie przydziału
    url = reverse('add_assignment')
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login" in resp.url

@pytest.mark.django_db
def test_add_assignment_post_creates_when_logged(logged_client, employee_jan, dept_sales, shift_morning):
    # ✅ Zalogowany może dodać nowy przydział
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
    # ✅ Sprawdza, że GET działa (albo redirect do login, albo formularz)
    url = reverse("assign_employees")
    resp = client.get(url)
    assert resp.status_code in (200, 302)

@pytest.mark.django_db
def test_assign_employees_post_assigns_when_logged(logged_client, dept_sales):
    # ✅ Algorytm działa i przypisuje pracowników do działów
    e1 = Employee.objects.create(first_name="A", last_name="A", status="available", hire_date=date(2024, 1, 1))
    e2 = Employee.objects.create(first_name="B", last_name="B", status="available", hire_date=date(2024, 1, 2))

    url = reverse("assign_employees")
    resp = logged_client.post(url)
    assert resp.status_code == 200

    e1.refresh_from_db()
    e2.refresh_from_db()
    assert e1.department.exists()
    assert e2.department.exists()

@pytest.mark.django_db
def test_delete_assignment_removes_assignment(logged_client, employee_jan, dept_sales, shift_morning):
    assignment = Assignment.objects.create(
        employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 5)
    )
    url = reverse("assignment_delete", args=[assignment.id])
    resp = logged_client.post(url)
    assert resp.status_code == 302
    assert resp.url == reverse("assignment_list")
    assert not Assignment.objects.filter(id=assignment.id).exists()


@pytest.mark.django_db
def test_assignment_delete_redirects_when_anon(client, employee_jan, dept_sales, shift_morning):
    """Anonimowy użytkownik -> redirect do /login/ i brak usunięcia."""
    a = Assignment.objects.create(
        employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 10)
    )
    url = reverse("assignment_delete", args=[a.id])
    resp = client.post(url)
    assert resp.status_code == 302
    assert "/login" in resp.url
    assert Assignment.objects.filter(id=a.id).exists()


