# ================== TESTY PROJEKTU SHIFT ALLOCATOR ==================
# Każda sekcja odpowiada widokowi. Testuję m.in.:
# - dostęp (zalogowany / niezalogowany / uprawnienia)
# - poprawne renderowanie formularzy i list
# - poprawne zapisy/edycje/usuwanie
# - filtrowanie i algorytm przydziałów
# ====================================================================

import pytest
from datetime import date, time
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from employees.models import Employee, Department, Shift, Assignment


# ================== FIKSTURY WSPÓLNE ==================
# Fikstury to takie „gotowce” do testów – tworzą użytkowników, klientów, obiekty w bazie.

@pytest.fixture
def client():
    return Client()  # niezalogowany klient

@pytest.fixture
def user(db):
    return User.objects.create_user(username="tester", password="pass12345")

@pytest.fixture
def logged_client(client, user):
    client.login(username="tester", password="pass12345")
    return client

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username="manager", password="pass123", is_staff=True)

@pytest.fixture
def staff_client(client, staff_user):
    client.login(username="manager", password="pass123")
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


# ================== EMPLOYEES ==================

# employee_list (lista pracowników, publiczna)
@pytest.mark.django_db
def test_employee_list_returns_200_for_anon(client):
    # ✅ niezalogowany użytkownik widzi listę pracowników
    url = reverse('employee_list')
    resp = client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_employee_list_search_and_sort_works(client, employee_jan):
    # ✅ sprawdzam czy działa wyszukiwanie i sortowanie
    url = reverse('employee_list')
    resp = client.get(url, {"q": "Kow", "sort": "desc"})
    assert b'Kowalski' in resp.content


# add_employee (dodawanie pracownika, wymaga loginu)
@pytest.mark.django_db
def test_add_employee_get_redirects_when_anon(client):
    # ❌ niezalogowany → redirect do login
    url = reverse('add_employee')
    resp = client.get(url)
    assert resp.status_code == 302

@pytest.mark.django_db
def test_add_employee_get_returns_200_when_logged(logged_client):
    # ✅ zalogowany widzi formularz dodawania
    url = reverse('add_employee')
    resp = logged_client.get(url)
    assert b'<form' in resp.content

@pytest.mark.django_db
def test_add_employee_post_creates_when_logged(logged_client):
    # ✅ zapisuje nowego pracownika
    url = reverse('add_employee')
    data = {'first_name': 'Jan', 'last_name': 'Kowalski', 'status': 'available', 'hire_date': '2024-01-01'}
    resp = logged_client.post(url, data)
    assert Employee.objects.filter(first_name='Jan').exists()

@pytest.mark.django_db
def test_add_employee_post_invalid_stays_on_form_when_logged(logged_client):
    # ❌ brak nazwiska → formularz się nie zapisze, zostaje na stronie
    url = reverse('add_employee')
    data = {'first_name': 'BezNazwiska', 'status': 'available', 'hire_date': '2024-01-01'}
    resp = logged_client.post(url, data)
    assert resp.status_code == 200
    assert Employee.objects.filter(first_name='BezNazwiska').count() == 0


# edit_employee (edycja pracownika, login required)
@pytest.mark.django_db
def test_edit_employee_get_redirects_when_anon(client, employee_jan):
    # ❌ niezalogowany nie ma dostępu
    url = reverse('edit_employee', args=[employee_jan.id])
    resp = client.get(url)
    assert resp.status_code == 302

@pytest.mark.django_db
def test_edit_employee_get_returns_200_when_logged(logged_client, employee_jan):
    # ✅ zalogowany widzi formularz edycji
    url = reverse('edit_employee', args=[employee_jan.id])
    resp = logged_client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_edit_employee_post_updates_when_logged(logged_client, employee_jan):
    # ✅ zmiana nazwiska i statusu działa
    url = reverse('edit_employee', args=[employee_jan.id])
    data = {'first_name': 'Jan', 'last_name': 'Zmieniony', 'status': 'holiday', 'hire_date': '2024-01-01'}
    logged_client.post(url, data)
    employee_jan.refresh_from_db()
    assert employee_jan.last_name == 'Zmieniony'


# delete_employee (usuwanie pracownika, login required)
@pytest.mark.django_db
def test_delete_employee_get_redirects_when_anon(client, employee_jan):
    # ❌ niezalogowany nie zobaczy strony usuwania
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = client.get(url)
    assert resp.status_code == 302

@pytest.mark.django_db
def test_delete_employee_get_confirmation_when_logged(logged_client, employee_jan):
    # ✅ zalogowany widzi potwierdzenie usunięcia
    url = reverse('delete_employee', args=[employee_jan.id])
    resp = logged_client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_delete_employee_post_removes_when_logged(logged_client, employee_jan):
    # ✅ po zatwierdzeniu pracownik znika z bazy
    url = reverse('delete_employee', args=[employee_jan.id])
    logged_client.post(url)
    assert not Employee.objects.filter(id=employee_jan.id).exists()


# ================== ASSIGNMENTS ==================

# assignment_list
@pytest.mark.django_db
def test_assignment_list_redirects_when_anon(client):
    # ❌ niezalogowany nie wejdzie na listę przydziałów
    url = reverse('assignment_list')
    resp = client.get(url)
    assert resp.status_code == 302

@pytest.mark.django_db
def test_assignment_list_returns_200_when_logged(logged_client):
    # ✅ zalogowany widzi listę przydziałów
    url = reverse('assignment_list')
    resp = logged_client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_assignment_list_filters_by_date_when_logged(logged_client, employee_jan, dept_sales, shift_morning):
    # ✅ filtrowanie po dacie działa
    Assignment.objects.create(employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 1))
    Assignment.objects.create(employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 2))
    url = reverse('assignment_list')
    resp = logged_client.get(url, {"date": "2025-01-02"})
    html = resp.content.decode()
    assert "2025-01-02" in html and "2025-01-01" not in html

# add_assignment
@pytest.mark.django_db
def test_add_assignment_get_redirects_when_anon(client):
    # ❌ niezalogowany nie zobaczy formularza dodawania
    url = reverse('add_assignment')
    resp = client.get(url)
    assert resp.status_code == 302

@pytest.mark.django_db
def test_add_assignment_post_creates_when_logged(logged_client, employee_jan, dept_sales, shift_morning):
    # ✅ zalogowany może dodać nowy przydział
    url = reverse('add_assignment')
    resp = logged_client.post(url, {
        "employee": employee_jan.id,
        "department": dept_sales.id,
        "shift": shift_morning.id,
        "date": "2025-01-03",
    })
    assert Assignment.objects.filter(date=date(2025, 1, 3)).exists()

# assignment_delete
@pytest.mark.django_db
def test_delete_assignment_removes_assignment(logged_client, employee_jan, dept_sales, shift_morning):
    # ✅ usuwanie przydziału działa
    a = Assignment.objects.create(employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 5))
    url = reverse("assignment_delete", args=[a.id])
    logged_client.post(url)
    assert not Assignment.objects.filter(id=a.id).exists()

@pytest.mark.django_db
def test_assignment_delete_redirects_when_anon(client, employee_jan, dept_sales, shift_morning):
    # ❌ niezalogowany nie może usuwać
    a = Assignment.objects.create(employee=employee_jan, department=dept_sales, shift=shift_morning, date=date(2025, 1, 10))
    url = reverse("assignment_delete", args=[a.id])
    resp = client.post(url)
    assert Assignment.objects.filter(id=a.id).exists()


# ================== ALGORYTM PRZYDZIAŁU ==================

@pytest.mark.django_db
def test_assign_employees_get_redirects_or_renders_form(client):
    # ✅ GET dla algorytmu → albo redirect do login, albo renderuje stronę
    url = reverse("assign_employees")
    resp = client.get(url)
    assert resp.status_code in (200, 302)

@pytest.mark.django_db
def test_assign_employees_post_assigns_when_logged(logged_client, dept_sales):
    # ✅ POST do algorytmu coś przypisuje / zwraca stronę
    Employee.objects.create(first_name="A", last_name="A", status="available", hire_date=date(2024, 1, 1))
    Employee.objects.create(first_name="B", last_name="B", status="available", hire_date=date(2024, 1, 2))
    url = reverse("assign_employees")
    resp = logged_client.post(url)
    assert resp.status_code == 200


# ================== DEPARTMENTS (CRUD, staff required) ==================

# DepartmentListView
@pytest.mark.django_db
def test_department_list_requires_login(client):
    # ❌ niezalogowany → redirect do login
    url = reverse("department_list")
    resp = client.get(url)
    assert resp.status_code == 302

@pytest.mark.django_db
def test_department_list_as_staff_shows_departments(staff_client, dept_sales):
    # ✅ staff widzi listę działów
    url = reverse("department_list")
    resp = staff_client.get(url)
    assert b"Sales" in resp.content

# DepartmentCreateView
@pytest.mark.django_db
def test_department_create_shows_form_for_staff(staff_client):
    # ✅ staff widzi formularz dodawania działu
    url = reverse("department_add")
    resp = staff_client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_department_create_creates_new_department_for_staff(staff_client):
    # ✅ staff może dodać nowy dział
    url = reverse("department_add")
    staff_client.post(url, {"name": "Logistics", "capacity": 3})
    assert Department.objects.filter(name="Logistics").exists()

# DepartmentUpdateView
@pytest.mark.django_db
def test_department_edit_loads_form_for_staff(staff_client, dept_sales):
    # ✅ staff widzi formularz edycji
    url = reverse("department_edit", args=[dept_sales.id])
    resp = staff_client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_department_edit_changes_data_for_staff(staff_client, dept_sales):
    # ✅ staff może edytować dane działu
    url = reverse("department_edit", args=[dept_sales.id])
    staff_client.post(url, {"name": "Sales & Service", "capacity": 10})
    dept_sales.refresh_from_db()
    assert dept_sales.name == "Sales & Service"

# DepartmentDeleteView
@pytest.mark.django_db
def test_department_delete_confirmation_page_for_staff(staff_client, dept_sales):
    # ✅ staff widzi stronę potwierdzenia usunięcia
    url = reverse("department_delete", args=[dept_sales.id])
    resp = staff_client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_department_delete_removes_object_for_staff(staff_client, dept_sales):
    # ✅ staff usuwa dział → nie ma go w bazie
    url = reverse("department_delete", args=[dept_sales.id])
    staff_client.post(url)
    assert not Department.objects.filter(id=dept_sales.id).exists()
