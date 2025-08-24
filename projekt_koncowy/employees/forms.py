from django import forms
from .models import Employee, Assignment, Department


class EmployeeForm(forms.ModelForm):
    # ✅ ManyToMany → wielokrotny wybór (checkboxy)
    department = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Departments",
        help_text="Zaznacz jeden lub więcej działów."
    )

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'department', 'status', 'hire_date']
        widgets = {
            # ✅ kalendarzyk HTML5
            'hire_date': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'status': 'Status',
            'hire_date': 'Hire date',
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['employee', 'department', 'shift', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {
            'employee': 'Employee',
            'department': 'Department',
            'shift': 'Shift',
            'date': 'Date',
        }
