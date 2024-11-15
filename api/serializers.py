from rest_framework import serializers
from project.models import Project, Task, Activity, TeamMember

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at', 'updated_at', 'hourly_rate', 'is_active']
        read_only_fields = ['id', 'is_active']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'status', 'hours_count', 'total_price', 'date_for', 'is_billable']
        read_only_fields = ['id', 'status']

class ProjectDetailSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True) 

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'hourly_rate', 'is_active', 'tasks']

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'project', 'task', 'user', 'action', 'details', 'timestamp']

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'project', 'status', 'is_active']