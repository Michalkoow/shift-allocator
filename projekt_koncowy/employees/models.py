from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nazwa działu
    capacity = models.IntegerField()  # Ile osób maksymalnie może być w dziale

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ManyToManyField(Department, blank=True)  # Pracownik może być przypisany do wielu działów
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('vacation', 'On Vacation'),
            ('sick', 'Sick Leave'),
            ('absent', 'Absent')
        ],
        default='available'
    )
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

