from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    def __str__(self):
        return self.username
