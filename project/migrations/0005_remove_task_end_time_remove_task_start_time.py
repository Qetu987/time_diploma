# Generated by Django 5.1.1 on 2024-10-18 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_task_end_time_task_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='task',
            name='start_time',
        ),
    ]
