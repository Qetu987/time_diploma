from django.contrib import admin
from project.models import *

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'hourly_rate', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username', 'hourly_rate')
    list_filter = ('is_active',)
    date_hierarchy = 'created_at'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'status')
    search_fields = ('user__username', 'project__name')
    list_filter = ('status',)
    raw_id_fields = ('user', 'project')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'assigned_to', 'status', 'hours_count', 'total_price', 'is_billable', 'created_at')
    search_fields = ('name', 'project__name', 'assigned_to__username')
    list_filter = ('status', 'is_billable')
    date_hierarchy = 'created_at'
    raw_id_fields = ('project', 'assigned_to')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'project', 'task', 'timestamp')
    search_fields = ('user__username', 'project__name', 'task__name')
    list_filter = ('action', 'timestamp')
    date_hierarchy = 'timestamp'
    raw_id_fields = ('user', 'project', 'task')