from django.contrib import admin
from user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'status', 'hourly_rate', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('status', 'is_active')