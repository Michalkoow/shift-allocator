import random
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projekt_koncowy.settings")
django.setup()

from employees.models import Employee, Department
from faker import Faker

fake = Faker()

departments = list(Department.objects.all())

statuses = ["available", "holiday", "sick", "absent", "day_off"]

for _ in range(50):
    first_name = fake.first_name()
    last_name = fake.last_name()
    status = random.choice(statuses)
    hire_date = fake.date_between(start_date="-10y", end_date="today") 


    employee = Employee.objects.create(
        first_name=first_name,
        last_name=last_name,
        status=status,
        hire_date=hire_date 

    )
    if departments:
        employee.department.set(
            random.sample(departments, k=random.randint(1, min(3, len(departments))))
        )
print("✅ Dodano 50 pracowników!")
