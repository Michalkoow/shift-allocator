from django.shortcuts import render, redirect
from .models import Employee  # Usunięcie błędnego importu assign_employees
from .forms import EmployeeForm
from .utils import assign_employees  # Poprawny import funkcji z utils.py

def employee_list(request):
    employees = Employee.objects.all()
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
