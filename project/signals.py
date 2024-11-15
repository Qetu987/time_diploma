from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, Task, Activity, TeamMember

@receiver(post_save, sender=Project)
def create_project_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            project=instance,
            user=instance.owner,
            action='created_project',
            details=f"Project '{instance.name}' created. Project rate: {instance.hourly_rate}"
        )
    else:
        if instance.is_active:
            Activity.objects.create(
                project=instance,
                user=instance.owner,
                action='updated_project',
                details=f"Project '{instance.name}' updated. Project rate: {instance.hourly_rate}"
            )
        else:
            Activity.objects.create(
                project=instance,
                user=instance.owner,
                action='project_inactive',
                details=f"Project '{instance.name}' deactivate."
            )

@receiver(post_save, sender=Task)
def create_task_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            project=instance.project,
            task=instance,
            user=instance.assigned_to,
            action='created_task',
            details=f"Task '{instance.name}' created in project '{instance.project}'."
        )
    else:
        Activity.objects.create(
            project=instance.project,
            task=instance,
            user=instance.assigned_to,
            action='updated_task',
            details=f"Task '{instance.name}' updated in project '{instance.project}'."
        )

@receiver(post_save, sender=TeamMember)
def add_member_activity(sender, instance, created, **kwargs):
    print('hello')
    if created:
        Activity.objects.create(
            project=instance.project,
            user=instance.user,
            action='added_member',
            details=f"User '{instance.user.username}' added to project '{instance.project.name}' by '{instance.project.owner}'."
        )
    else:
        if instance.is_active:
            Activity.objects.create(
                project=instance.project,
                user=instance.user,
                action='activate_member',
                details=f"User '{instance.user.username}' activate in project '{instance.project.name}' by '{instance.project.owner}'."
            )
        else:
            Activity.objects.create(
                project=instance.project,
                user=instance.user,
                action='deactivate_member',
                details=f"User '{instance.user.username}' deactivate from project '{instance.project.name}' by '{instance.project.owner}'."
            )
