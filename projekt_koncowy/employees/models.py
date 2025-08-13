from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ===== 1. model:Department=====
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nazwa działu
    capacity = models.IntegerField()                      # Maksymalna liczba osób w dziale

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# ===== 2. model:Employee=====
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    department = models.ManyToManyField(Department, blank=True)  # Pracownik może być w wielu działach
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('holiday',   'Holiday'),
            ('sick',      'Sick Leave'),
            ('absent',    'Absent'),
            ('off',       'Day off'),
        ],
        default='available'
    )
    hire_date = models.DateField()

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# ===== 3. model:Shift=====
class Shift(models.Model):
    name       = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time   = models.TimeField()

    class Meta:
        ordering = ["start_time", "name"]

    def __str__(self):
        return self.name

# ===== 4. model:Assignment =====
class Assignment(models.Model):
    employee   = models.ForeignKey(Employee,   on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    shift      = models.ForeignKey(Shift,      on_delete=models.CASCADE)
    date       = models.DateField()

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} {self.shift}, {self.date}, {self.department.name}"


# ===== 5. model: UserProfile (OneToOne z wbudowanym User) =====
class UserProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department   = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    bio          = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profil: {self.user.username}"


# Automatyczne tworzenie profilu po utworzeniu użytkownika
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # Jeśli nowy użytkownik — utwórz profil
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Dla istniejących — upewnij się, że profil istnieje
        UserProfile.objects.get_or_create(user=instance)
