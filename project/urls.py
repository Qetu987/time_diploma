from django.urls import path
from project.views import (
    DashboardView, CreateProject, ProjectsListView, 
    ProjectDetailView, CreateTask, EditProjectView, 
    AddTeamMemberView, RemoveMemberView, ProjectActivityView,
    ActivityView, ReportView, ProjectReportView
    )


urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('projects/', ProjectsListView.as_view(), name='projects'),
    path("create_project/", CreateProject.as_view(), name='create_project'),
    
    path('<int:pk>/', ProjectDetailView.as_view(), name='project'),
    path('<int:project_id>/edit/', EditProjectView.as_view(), name='edit_project'),
    path('<int:project_id>/create_task/', CreateTask.as_view(), name='create_task'),
    path('activity/', ActivityView.as_view(), name='activity'),
    path('<int:project_id>/activity/', ProjectActivityView.as_view(), name='project_activity'),

    path('report/', ReportView.as_view(), name='report'),
    path('<int:project_id>/report/', ProjectReportView.as_view(), name='project_report'),
    
    path('<int:project_id>/add_team_member/', AddTeamMemberView.as_view(), name='add_member'),
    path('<int:project_id>/remove_member/<int:member_id>/', RemoveMemberView.as_view(), name='remove_member'),
]