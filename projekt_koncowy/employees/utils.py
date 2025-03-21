import random
from zoneinfo import available_timezones

from .models import Employee, Department

def assign_employees():
    departments = list(Department.objects.all())
    employees = list(Employee.objects.filter(status__iexact='available'))


    # Czyszczenie wcześniejszych przypisań
    for emp in employees:
        emp.department.clear()

    random.shuffle(employees)  # losujemy kolejność pracowników

    assignments = {}  # {nazwa_działu: [lista pracowników]}
    history = {}  # {employee_id: [lista_nazw_działów]}

    while employees:
        for department in departments:
            if not employees:
                break  # jeśli skończyli się pracownicy

            if department.capacity > department.employee_set.count():
                for emp in employees:
                    # lista działów, w których już był pracownik (jeśli brak, to pusty)
                    previous_departments = history.get(emp.id, [])

                    # Sprawdź, czy nie był już przypisany do tego działu w tym tygodniu
                    if department.name not in previous_departments:
                        emp.department.add(department)
                        emp.save()

                        # Zapisz przypisanie do historii
                        if emp.id not in history:
                            history[emp.id] = []
                        history[emp.id].append(department.name)

                        # Zapisz przypisanie do zwrotu
                        if department.name not in assignments:
                            assignments[department.name] = []
                        assignments[department.name].append(f"{emp.first_name} {emp.last_name}")


                        # Usuń pracownika z listy do przydziału
                        employees.remove(emp)
                        break  # przechodzimy do kolejnego działu

    return assignments
