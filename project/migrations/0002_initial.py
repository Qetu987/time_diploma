# Generated by Django 5.1.1 on 2024-09-27 15:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='user.user'),
        ),
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_projects', to='user.user'),
        ),
        migrations.AddField(
            model_name='position',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='project.project'),
        ),
        migrations.AddField(
            model_name='activity',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='project.project'),
        ),
        migrations.AddField(
            model_name='task',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='user.user'),
        ),
        migrations.AddField(
            model_name='task',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='project.project'),
        ),
        migrations.AddField(
            model_name='activity',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activities', to='project.task'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='positions',
            field=models.ManyToManyField(related_name='team_members', to='project.position'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='project.project'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_roles', to='user.user'),
        ),
    ]
