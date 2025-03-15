from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee  # Usunięcie błędnego importu assign_employees
from .forms import EmployeeForm
from .utils import assign_employees  # Poprawny import funkcji z utils.py

def employee_list(request):
    employees = Employee.objects.all()
    print(f"Pobrani pracownicy w widoku: {employees}")  # Debugowanie - sprawdzenie co Django widzi
    return render(request, 'employees/employee_list.html', {'employees': employees})


def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()  # Zapisz nowego pracownika do bazy danych
            return redirect('employee_list')  # Przekierowanie do listy pracowników
    else:
        form = EmployeeForm()

    return render(request, 'employees/add_employee.html', {'form': form})

def assign_employees_view(request):
    assignments = assign_employees()  # Wywołanie funkcji do przypisania pracowników
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