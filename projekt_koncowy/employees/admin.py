from django.contrib import admin
from .models import Employee, Shift, Assignment


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "get_departments", "status", "hire_date")
    list_filter = ("status",)
    search_fields = ("first_name", "last_name")

    def get_departments(self, obj):
        return ", ".join([dept.name for dept in obj.department.all()])

    get_departments.short_description = "Departments"  # Nazwa kolumny w Django Admin


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("employee", "department", "shift", "date")
    list_filter = ("department", "shift", "date")
    search_fields = ("employee__first_name", "employee__last_name")

