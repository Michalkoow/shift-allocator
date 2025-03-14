from .models import Employee, Department
import random


def assign_employees():
    """Przydziela pracowników do działów według dostępności i sprawiedliwej rotacji."""

    departments = Department.objects.all()
    employees = list(Employee.objects.filter(status="available").order_by('?'))  # Zamieniamy QuerySet na listę

    # Czyszczenie wcześniejszych przypisań
    for emp in employees:
        emp.department.clear()  # Usuwamy wcześniejsze przypisania

    assignments = {}  # Słownik {dział: lista_pracowników}

    # Przydzielamy pracowników do działów rotacyjnie
    department_cycle = list(departments)  # Lista działów do rotacyjnego przypisywania

    while employees:
        for department in department_cycle:
            if not employees:  # Jeśli skończyli się dostępni pracownicy, przerywamy
                break

            if department.capacity > len(department.employee_set.all()):  # Sprawdzamy czy jest miejsce
                emp = employees.pop(0)  # Pobieramy pierwszego pracownika z listy
                emp.department.add(department)  # Przypisujemy go do działu
                emp.save()  # Zapisujemy zmianę

                # Dodajemy do listy przypisanych
                if department.name not in assignments:
                    assignments[department.name] = []
                assignments[department.name].append(f"{emp.first_name} {emp.last_name}")

    return assignments  # Zwracamy wynik przypisań
