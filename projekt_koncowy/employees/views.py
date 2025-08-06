from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Assignment
from .forms import EmployeeForm, AssignmentForm
from .utils import assign_employees
from django.core.paginator import Paginator



from django.db.models import Q

def employee_list(request):
    query = request.GET.get('q', '').strip()  # Pobranie i usunięcie białych znaków
    sort_order = request.GET.get('sort', 'asc')  # Pobranie parametru sortowania
    status_filter = request.GET.get('status', '')  # Pobranie statusu

    employees = Employee.objects.all()

    # Filtrowanie pracowników po nazwisku, imieniu, dziale
    if query:
        employees = employees.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(department__name__icontains=query)
        )

    # Filtrowanie po statusie
    if status_filter:
        employees = employees.filter(status=status_filter)

    # Sortowanie po nazwisku
    employees = employees.order_by("last_name") if sort_order == "asc" else employees.order_by("-last_name")

    # Paginacja - 20 pracowników na stronę
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
#         print("PRZYDZIAŁY:", assignments)  # 👀 Powinno się pojawić w terminalu!
#
#     return render(request, 'employees/assign_employees.html', {'assignments': assignments})

def assign_employees_view(request):
    print("✅ Otrzymano `POST`!")  # Powinno pojawić się w terminalu

    if request.method == "POST":
        assignments = assign_employees()  # Czy zwraca poprawne dane?
        print("📌 Wyniki przypisania:", assignments)  # Powinno pojawić się w terminalu
        return render(request, 'employees/assign_employees.html', {'assignments': assignments})

    return render(request, 'employees/assign_employees.html', {'assignments': None})



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

def add_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')

    else:
        form = AssignmentForm()

    return render(request, 'employees/add_assignment.html', {'form': form})


def assignment_list(request):
    date_filter = request.GET.get('date', '')  # pobranie daty z GET
    assignments = Assignment.objects.all().order_by('-date')

    # Filtrowanie po dacie
    if date_filter:
        assignments = assignments.filter(date=date_filter)

    # Paginacja - 10 przydziałów na stronę
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employees/assignment_list.html', {
        'assignments': page_obj,
        'date_filter': date_filter,
        'page_obj': page_obj
    })


