from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Task


class SignupForm(UserCreationForm):
    POSITION_CHOICES = (
        ('CEO', 'Chief Executive Officer'),
        ('COO', 'Chief Operating Officer'),
        ('CFO', 'Chief Financial Officer'),
        ('CMO', 'Chief Marketing Officer'),
        ('CIO', 'Chief Information Officer'),
        ('CTO', 'Chief Technology Officer'),
        ('OM', 'Operations Manager'),
        ('SM', 'Sales Manager'),
        ('AM', 'Account Manager'),
        ('MM', 'Marketing Manager'),
        ('PM', 'Project Manager'),
        ('GM', 'General Manager'),
        ('HRM', 'Human Resources Manager'),
        ('AA', 'Administrative Assistant'),
        ('PM', 'Product Manager'),
        ('CSR', 'Customer Service Representative'),
        ('AE', 'Account Executive'),
        ('FM', 'Financial Manager'),
        ('ED', 'Executive Director'),
        ('EA', 'Executive Assistants'),
        ('MS', 'Marketing Specialist'),
        ('SR', 'Sales Representative'),
        ('VP', 'Vice President'),
        ('FA', 'Financial Analyst'),
        ('BA', 'Business Analyst'),
        ('HRP', 'Human Resource Personnel'),
        ('ACC', 'Accountant'),
        ('ST', 'Staff'),
        ('IN', 'Intern'),
    )

    DIVISION_CHOICES = (
        ('leadership', 'Leadership'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('production', 'Production'),
        ('human_resources', 'Human Resources'),
        ('quality_management', 'Quality Management'),
        ('sales', 'Sales'),
        ('research_and_development', 'Research & Development'),
        ('legal', 'Legal'),
    )

    position = forms.ChoiceField(choices=POSITION_CHOICES, label='Position')
    division = forms.ChoiceField(choices=DIVISION_CHOICES, label='Division')

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'company', 'division', 'position']


class TaskForm(forms.ModelForm):
    TYPES_CHOICES = (
        ('Urgent and Important', 'Urgent and Important'),
        ('Not Urgent but Important', 'Not Urgent but Important'),
        ('Urgent but Not Important', 'Urgent but Not Important'),
        ('Not Urgent and Not Important', 'Not Urgent and Not Important'),
    )
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )

    types = forms.ChoiceField(choices=TYPES_CHOICES, label='Task type')

    class Meta:
        model = Task
        fields = ['task_name', 'start', 'deadline', 'assigned_to', 'types']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(TaskForm, self).__init__(*args, **kwargs)

        if current_user:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(company=current_user.company, division=current_user.division).exclude(id=current_user.id)


class UpdateProfileForm(forms.ModelForm):
    POSITION_CHOICES = (
        ('CEO', 'Chief Executive Officer'),
        ('COO', 'Chief Operating Officer'),
        ('CFO', 'Chief Financial Officer'),
        ('CMO', 'Chief Marketing Officer'),
        ('CIO', 'Chief Information Officer'),
        ('CTO', 'Chief Technology Officer'),
        ('OM', 'Operations Manager'),
        ('SM', 'Sales Manager'),
        ('AM', 'Account Manager'),
        ('MM', 'Marketing Manager'),
        ('PM', 'Project Manager'),
        ('GM', 'General Manager'),
        ('HRM', 'Human Resources Manager'),
        ('AA', 'Administrative Assistant'),
        ('PM', 'Product Manager'),
        ('CSR', 'Customer Service Representative'),
        ('AE', 'Account Executive'),
        ('FM', 'Financial Manager'),
        ('ED', 'Executive Director'),
        ('EA', 'Executive Assistants'),
        ('MS', 'Marketing Specialist'),
        ('SR', 'Sales Representative'),
        ('VP', 'Vice President'),
        ('FA', 'Financial Analyst'),
        ('BA', 'Business Analyst'),
        ('HRP', 'Human Resource Personnel'),
        ('ACC', 'Accountant'),
        ('ST', 'Staff'),
        ('IN', 'Intern'),
    )

    DIVISION_CHOICES = (
        ('leadership', 'Leadership'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('production', 'Production'),
        ('human_resources', 'Human Resources'),
        ('quality_management', 'Quality Management'),
        ('sales', 'Sales'),
        ('research_and_development', 'Research & Development'),
        ('legal', 'Legal'),
    )

    position = forms.ChoiceField(choices=POSITION_CHOICES, label='Position')
    division = forms.ChoiceField(choices=DIVISION_CHOICES, label='Division')

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'company', 'division', 'position']
