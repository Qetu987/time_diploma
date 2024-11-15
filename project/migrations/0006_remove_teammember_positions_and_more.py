# Generated by Django 5.1.1 on 2024-10-18 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_remove_task_end_time_remove_task_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teammember',
            name='positions',
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='hourly_rate',
        ),
        migrations.AddField(
            model_name='project',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.DeleteModel(
            name='Position',
        ),
    ]