from django.db import models
from user.models import User

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name="owned_projects", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    STATUS_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('reader', 'Reader'),
    ]

    user = models.ForeignKey(User, related_name="project_roles", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name="team_members", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.status})"


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name="tasks", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    hours_count = models.PositiveIntegerField(default=1)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_billable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_for = models.DateTimeField(blank=True, null=True,)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_billable and self.assigned_to:
            try:                
                self.total_price = self.hours_count * self.project.hourly_rate
            except TeamMember.DoesNotExist:
                self.total_price = 0
        else:
            self.total_price = 0
        super(Task, self).save(*args, **kwargs)


class Activity(models.Model):
    ACTION_CHOICES = [
        ('created_project', 'Created Project'),
        ('updated_project', 'Updated Project'),
        ('created_task', 'Created Task'),
        ('updated_task_status', 'Updated Task Status'),
        ('added_member', 'Added Member'),
        ('deactivate_member', 'Deactivate Member'),
        ('activate_member', 'Activate Member'),
        ('project_inactive', 'Marked Project as Inactive'),
    ]

    project = models.ForeignKey(Project, related_name="activities", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name="activities", null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, related_name="activities", on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} in {self.project.name} at {self.timestamp}"