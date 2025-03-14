from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "get_departments", "status", "hire_date")
    list_filter = ("status",)
    search_fields = ("first_name", "last_name")

    def get_departments(self, obj):
        return ", ".join([dept.name for dept in obj.department.all()])

    get_departments.short_description = "Departments"  # Nazwa kolumny w Django Admin
