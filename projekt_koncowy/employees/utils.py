import random
from .models import Employee, Department


def assign_employees():
    departments = list(Department.objects.all())
    employees = list(Employee.objects.filter(status__iexact='available'))

    print(f"Dostępne departamenty: {departments}")
    print(f"Pracownicy do przypisania: {employees}")

    # Czyszczenie wcześniejszych przypisań
    for emp in employees:
        emp.department.clear()

    random.shuffle(employees)  # losujemy kolejność pracowników

    assignments = {}  # {nazwa_działu: [lista pracowników]}
    assigned_count = {dep.name: 0 for dep in departments}  # Śledzimy liczbę przypisanych osób

    for emp in employees:
        available_departments = [dep for dep in departments if assigned_count[dep.name] < dep.capacity]

        if not available_departments:
            print(f"❌ Brak dostępnych miejsc dla {emp.first_name} {emp.last_name}")
            continue

        department = random.choice(available_departments)
        emp.department.add(department)
        emp.save()

        assigned_count[department.name] += 1  # Aktualizacja licznika przypisań

        print(f"Przypisano: {emp.first_name} {emp.last_name} -> {department.name}")

        if department.name not in assignments:
            assignments[department.name] = []
        assignments[department.name].append(f"{emp.first_name} {emp.last_name}")

    print(f"Ostateczne przypisania: {assignments}")
    return assignments
