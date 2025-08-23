from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Employee, Assignment
from .forms import EmployeeForm, AssignmentForm
from .utils import assign_employees


# === LISTA PRACOWNIKÓW (publiczna) ===
def employee_list(request):
    query = request.GET.get('q', '').strip()
    sort_order = request.GET.get('sort', 'asc')
    status_filter = request.GET.get('status', '')

    employees = Employee.objects.all()

    if query:
        employees = employees.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(department__name__icontains=query)
        )

    if status_filter:
        employees = employees.filter(status=status_filter)

    employees = employees.order_by("last_name") if sort_order == "asc" else employees.order_by("-last_name")

    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employees/employee_list.html', {
        'employees': page_obj,
        'query': query,
        'sort_order': sort_order,
        'status_filter': status_filter,
        'page_obj': page_obj
    })


# === CRUD PRACOWNIKÓW (chronione) ===
@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pracownik został dodany.")
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/add_employee.html', {'form': form})


@login_required
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Dane pracownika zaktualizowane.")
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/edit_employee.html', {'form': form, 'employee': employee})


@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Pracownik został usunięty.")
        return redirect('employee_list')
    return render(request, 'employees/delete_employee.html', {'employee': employee})


# === ALGORYTM PRZYDZIAŁU (chronione) ===
@login_required
def assign_employees_view(request):
    if request.method == "POST":
        assignments = assign_employees()
        return render(request, 'employees/assign_employees.html', {'assignments': assignments})
    return render(request, 'employees/assign_employees.html', {'assignments': None})


# === PRZYDZIAŁY (chronione) ===
@login_required
def add_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Przydział zapisany.")
            return redirect('assignment_list')
    else:
        form = AssignmentForm()
    return render(request, 'employees/add_assignment.html', {'form': form})


@login_required
def assignment_list(request):
    date_filter = request.GET.get('date', '')
    assignments = Assignment.objects.all().order_by('-date')

    if date_filter:
        assignments = assignments.filter(date=date_filter)

    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employees/assignment_list.html', {
        'assignments': page_obj,
        'date_filter': date_filter,
        'page_obj': page_obj
    })


@login_required
def assignment_delete(request, pk):
    """Usunięcie pojedynczego przydziału (potwierdzenie w modal/oknie lub od razu POST z listy)."""
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Przydział usunięty.")
        return redirect('assignment_list')

    return render(request, 'employees/delete_assignment.html', {'assignment': assignment})


# === REJESTRACJA (publiczna) ===
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Konto utworzone. Zaloguj się.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'employees/register.html', {'form': form})
