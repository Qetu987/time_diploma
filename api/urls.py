from django.urls import path
from api.views import ProjectListCreateAPIView, ProjectDetailAPIView, TaskCreateAPIView, ProjectActivityAPIView, AddTeamMemberAPIView, ProjectTasksAPIView, ProjectUsersAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('projects/', ProjectListCreateAPIView.as_view(), name='project-list'),
    path('projects/<int:project_id>/', ProjectDetailAPIView.as_view(), name='project_detail_api'),
    path('projects/create/', ProjectListCreateAPIView.as_view(), name='project_list_create'),
    path('project/activities/', ProjectActivityAPIView.as_view(), name='project_activity'),
    path('projects/get_tasks/', ProjectTasksAPIView.as_view(), name='project_tasks'),
    path('projects/<int:project_id>/tasks/', TaskCreateAPIView.as_view(), name='task_create'),
    path('projects/<int:project_id>/add-member/', AddTeamMemberAPIView.as_view(), name='add_team_member'),
    path('projects/<int:project_id>/users/', ProjectUsersAPIView.as_view(), name='project_users'),
]