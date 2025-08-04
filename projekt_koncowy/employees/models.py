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
            ('holiday', 'Holiday'),
            ('sick', 'Sick Leave'),
            ('absent', 'Absent'),
            ('off', 'Day off')
        ],
        default='available'
    )
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Shift(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name


class Assignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} {self.shift}, {self.date}, {self.department.name}"

