from django import forms
from project.models import Project, Task, TeamMember 
from user.models import User 

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'hourly_rate', 'description']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'date_for', 'hours_count', 'is_billable']

class AddMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['id']


class AddTeamMemberForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label="Username")