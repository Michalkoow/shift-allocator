from django import forms
from .models import Employee, Assignment


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'department', 'status', 'hire_date']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'})
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['employee', 'department', 'shift', 'date']
