from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee  # Usunięcie błędnego importu assign_employees
from .forms import EmployeeForm
from .utils import assign_employees  # Poprawny import funkcji z utils.py
from django.core.paginator import Paginator
from .utils import assign_employees  # zakładamy, że funkcja jest w pliku utils.py

from django.shortcuts import render
from .models import Employee

def employee_list(request):
    query = request.GET.get('q', '')  # Pobranie wartości z paska wyszukiwania
    sort_order = request.GET.get('sort', 'asc')  # Pobranie parametru sortowania
    employees = Employee.objects.all()

    # Filtrowanie pracowników
    if query:
        employees = employees.filter(
            first_name__icontains=query
        ) | employees.filter(
            last_name__icontains=query
        ) | employees.filter(
            department__name__icontains=query
        ).distinct()

    # Sortowanie po nazwisku
    if sort_order == "asc":
        employees = employees.order_by("last_name")
    else:
        employees = employees.order_by("-last_name")  # Malejąco

    # Paginacja - 20 pracowników na stronę
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employees/employee_list.html', {
        'employees': page_obj,  # Teraz `employees` zawiera tylko bieżącą stronę
        'query': query,
        'sort_order': sort_order,
        'page_obj': page_obj
    })


def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()  # Zapisz nowego pracownika do bazy danych
            return redirect('employee_list')  # Przekierowanie do listy pracowników
    else:
        form = EmployeeForm()

    return render(request, 'employees/add_employee.html', {'form': form})

# def assign_employees_view(request):
#     assignments = None
#
#     if request.method == "POST":
#         assignments = assign_employees()
#
#     return render(request, 'employees/assign_employees.html', {'assignments': assignments})


def assign_employees_view(request):
    assignments = None

    if request.method == "POST":
        assignments = assign_employees()
        print("PRZYDZIAŁY:", assignments)  # <-- ważne

    return render(request, 'employees/assign_employees.html', {'assignments': assignments})




def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)  # Pobranie pracownika
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')  # Powrót do listy pracowników
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/edit_employee.html', {'form': form, 'employee': employee})

# Usuwanie pracownika
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')

    return render(request, 'employees/delete_employee.html', {'employee': employee})