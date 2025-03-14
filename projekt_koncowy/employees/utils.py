from .models import Employee, Department
import random


def assign_employees():
    """Przydziela pracowników do działów według dostępności i rotacji."""

    departments = Department.objects.all()
    employees = Employee.objects.filter(status="available").order_by('?')  # Losowa kolejność dla rotacji

    assignments = {}  # Słownik {dział: lista_pracowników}

    for department in departments:
        available_spots = department.capacity
        assigned = employees[:available_spots]  # Wybieramy pierwszych X pracowników
        employees = employees[available_spots:]  # Usuwamy już przypisanych

        for emp in assigned:
            emp.department.add(department)  # Przypisujemy pracownika do działu
            emp.save()

        assignments[department.name] = [f"{e.first_name} {e.last_name}" for e in assigned]

    return assignments  # Zwracamy listę przydzielonych osób do każdego działu
