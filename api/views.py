from rest_framework import generics
from api.serializers import ProjectSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from project.models import Project, Task, Activity, TeamMember
from user.models import User
from .serializers import ProjectSerializer, ProjectDetailSerializer, TaskSerializer, ActivitySerializer
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from datetime import datetime


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True)
        ).distinct().order_by('-updated_at')
    

class ProjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        projects = Project.objects.filter(
            id=project_id,
            is_active=True
        ).filter(
            Q(owner=request.user) | Q(team_members__user=request.user, team_members__is_active=True)
        ).distinct()

        if projects.count() > 1:
            return Response({"error": "Multiple projects found. Please check database integrity."}, status=500)
        elif not projects.exists():
            return Response({"error": "Project not found."}, status=404)

        project = projects.first()
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)
    

class ProjectListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True)
        ).distinct().order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)

        user = self.request.user
        if not (project.owner == user or project.team_members.filter(user=user, is_active=True).exists()):
            raise ValidationError("You do not have permission to create tasks for this project.")

        serializer.save(project=project, assigned_to=user)

class ProjectActivityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')

        if not project_id:
            raise ValidationError({'detail': 'Project ID is required.'})

        project = get_object_or_404(
            Project,
            id=project_id,
            is_active=True
        )
        user = request.user

        if not (project.owner == user or project.team_members.filter(user=user, is_active=True).exists()):
            raise ValidationError({'detail': 'You do not have access to this project.'})

        activities = Activity.objects.filter(project=project).order_by('-timestamp')

        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    

class AddTeamMemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        username = request.data.get('username')
        status = request.data.get('status', 'editor')

        if not username:
            raise ValidationError({"detail": "Username is required."})

        project = get_object_or_404(Project, id=project_id, is_active=True)

        if project.owner != request.user:
            raise ValidationError({"detail": "You do not have permission to add members to this project."})
        
        user = get_object_or_404(User, username=username)

        team_member, created = TeamMember.objects.get_or_create(user=user, project=project)
        if not created:
            if not team_member.is_active:
                team_member.is_active = True
                team_member.status = status
                team_member.save()
                return Response({"detail": f"User '{username}' has been reactivated in the project."})
            else:
                raise ValidationError({"detail": f"User '{username}' is already an active member of the project."})

        team_member.status = status
        team_member.save()

        return Response({"detail": f"User '{username}' has been added to the project with status '{status}'."})
    

class ProjectTasksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.data.get('project_id')
        assigned_to = request.data.get('assigned_to')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not project_id:
            raise ValidationError({"detail": "Project ID is required."})

        project = get_object_or_404(Project, id=project_id, is_active=True)
        user = request.user
        if not (project.owner == user or project.team_members.filter(user=user, is_active=True).exists()):
            raise ValidationError({"detail": "You do not have access to this project."})

        tasks = Task.objects.filter(project=project, is_active=True)

        if assigned_to:
            tasks = tasks.filter(assigned_to__id=assigned_to)

        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                tasks = tasks.filter(date_for__gte=start_date)
            except ValueError:
                raise ValidationError({"detail": "Invalid start_date format. Use YYYY-MM-DD."})

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                tasks = tasks.filter(date_for__lte=end_date)
            except ValueError:
                raise ValidationError({"detail": "Invalid end_date format. Use YYYY-MM-DD."})

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    

class ProjectUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, is_active=True)
        user = request.user
        if not (project.owner == user or project.team_members.filter(user=user, is_active=True).exists()):
            raise ValidationError({"detail": "You do not have access to this project."})

        owner = project.owner 
        members = TeamMember.objects.filter(project=project, is_active=True).select_related('user')

        users = [{'id': owner.id, 'username': owner.username, 'email': owner.email, 'role': 'owner'}]
        for member in members:
            users.append({
                'id': member.user.id,
                'username': member.user.username,
                'email': member.user.email,
                'role': member.status
            })

        return Response(users)