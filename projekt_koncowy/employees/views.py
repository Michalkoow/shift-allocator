from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

import datetime
from .models import Employee, Assignment, Department, Shift
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
        ).distinct()  # unikamy duplikatów przy M2M

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


# === DZIAŁY (lista + CRUD) ===
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = "employees/department_list.html"
    context_object_name = "departments"


class DepartmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Department
    fields = ['name', 'capacity']
    template_name = "employees/department_form.html"
    success_url = reverse_lazy("department_list")

    def test_func(self):
        return self.request.user.is_staff


class DepartmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Department
    fields = ['name', 'capacity']
    template_name = "employees/department_form.html"  # ten sam szablon co CreateView
    success_url = reverse_lazy("department_list")

    def test_func(self):
        return self.request.user.is_staff


class DepartmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Department
    template_name = "employees/department_confirm_delete.html"
    success_url = reverse_lazy("department_list")

    def test_func(self):
        return self.request.user.is_staff


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
    """
    GET  -> formularz (data + zmiana) i ewentualny podgląd przydziałów
    POST (action=preview) -> generuje PODGLĄD (bez zapisu)
    POST (action=save)    -> generuje i ZAPISUJE do Assignment, potem redirect na listę
    """
    if request.method == "POST":
        action = request.POST.get("action", "preview")
        date_str = request.POST.get("date")        # 'YYYY-MM-DD'
        shift_id = request.POST.get("shift")

        # Zawsze generujemy wynik algorytmu (podgląd lub do zapisu)
        result = assign_employees()  # np. {Department (lub nazwa): [Employee, ...]}

        # Tylko podgląd
        if action == "preview":
            return render(
                request,
                'employees/assign_employees.html',
                {
                    'assignments': result,
                    'shifts': Shift.objects.all(),
                    'date': date_str,
                    'selected_shift_id': shift_id,
                }
            )

        # Zapis do bazy
        errors = []
        if not date_str:
            errors.append("Wybierz datę.")
        if not shift_id:
            errors.append("Wybierz zmianę.")
        if errors:
            for e in errors:
                messages.error(request, e)
            return render(
                request,
                'employees/assign_employees.html',
                {
                    'assignments': result,
                    'shifts': Shift.objects.all(),
                    'date': date_str,
                    'selected_shift_id': shift_id,
                }
            )

        target_date = datetime.date.fromisoformat(date_str)
        shift = get_object_or_404(Shift, pk=shift_id)

        created = 0

        def resolve_employee(item):
            # 1) już obiekt Employee
            if isinstance(item, Employee):
                return item
            # 2) identyfikator (int/str z cyframi)
            if isinstance(item, int) or (isinstance(item, str) and item.isdigit()):
                return Employee.objects.filter(pk=int(item)).first()
            # 3) string "Imię Nazwisko" (lub wieloczłonowe nazwisko)
            if isinstance(item, str):
                parts = item.strip().split()
                if len(parts) >= 2:
                    first = parts[0]
                    last = " ".join(parts[1:])
                    return Employee.objects.filter(first_name=first, last_name=last).first()
                # fallback: spróbuj po samym imieniu
                return Employee.objects.filter(first_name=item.strip()).first()
            return None

        for dept_key, employees in (result or {}).items():
            # dział: obiekt lub nazwa
            if isinstance(dept_key, Department):
                dept = dept_key
            else:
                dept = Department.objects.filter(name=str(dept_key)).first()
            if not dept:
                continue  # nie znaleziono działu – pomiń

            for emp_item in employees:
                employee = resolve_employee(emp_item)
                if not employee:
                    continue  # nie udało się zmapować pracownika

                Assignment.objects.create(
                    employee=employee,
                    department=dept,
                    shift=shift,
                    date=target_date,
                )
                created += 1

        messages.success(request, f"Zapisano {created} przydziałów na {target_date} (zmiana: {shift.name}).")
        return redirect('assignment_list')

    # GET – pusty formularz + lista zmian
    return render(
        request,
        'employees/assign_employees.html',
        {
            'assignments': None,
            'shifts': Shift.objects.all(),
            'date': datetime.date.today().isoformat()
        }
    )


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
