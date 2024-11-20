from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.views.generic.base import View
from django.contrib.auth.models import AnonymousUser
from project.forms import ProjectForm, ProjectForm, TaskForm, AddTeamMemberForm
from project.models import Project, TeamMember, Task, Activity
from user.models import User
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.db.models import Sum, Q, Count, F, Avg
from urllib.parse import urlparse
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound, JsonResponse


class BasicDataView(View):
    template_name = None
    anonimys = AnonymousUser()
    header_menu = [
        ('Dashboard', 'dashboard'),
        ('Projects', 'projects'),
        ('Teams', 'projects'),
        ('Activity', 'activity'),
        ('Reports', 'projects'),
    ]

    def redirect_to_curent_page(self, request):
        referer_url = request.META.get('HTTP_REFERER')

        if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
            return HttpResponseRedirect(referer_url)
        else:
            return redirect('dashboard')

    def get_data(self, request):
        context = {
            'header_menu': self.header_menu,
            'user_data': request.user,
        }
        return context

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            raise Http404("Page not found")
        
        elif 'pk' in kwargs:
            context = self.get_data(request, kwargs.get('pk'))
        elif 'project_id' in kwargs:
            context = self.get_data(request, kwargs.get('project_id'))
        else:
            context = self.get_data(request)
        return render(request, self.template_name, context)


class DashboardView(BasicDataView):
    template_name = "project/dashboard.html"
    page_name = "Dashboard"
    active_page = "Dashboard"

    def get_projects(self, user):
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True), 
            is_active=True
        ).distinct().order_by('-updated_at')[:6]

        projects_list = []
        for project in projects:
            task_count = Task.objects.filter(project=project, is_active=True).count()
            total_sum = Task.objects.filter(project=project, is_active=True).aggregate(
                total=Sum('total_price')
            )['total'] or 0

            project_data = {
                'task_count': task_count,
                'total_sum': total_sum,
                'project': project,
            }

            projects_list.append(project_data)
            
        return projects_list
    
    def get_task_per_day(self, user):
        today = now().date()
        start_of_month = today.replace(day=1)

        user_projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True), 
            is_active=True
        ).distinct().order_by('-updated_at')

        tasks_by_day = Task.objects.filter(
            is_active=True,
            project__in=user_projects,
            date_for__gte=start_of_month
        ).exclude(date_for__isnull=True).values('date_for__date').annotate(
            count=Count('id')
        ).order_by('date_for__date')

        labels = []
        data = []

        date_range = [start_of_month + timedelta(days=x) for x in range((today - start_of_month).days + 1)]
        tasks_by_day_dict = {entry['date_for__date']: entry['count'] for entry in tasks_by_day}
        for date in date_range:
            labels.append(date.strftime('%Y-%m-%d'))
            data.append(tasks_by_day_dict.get(date, 0))

        return {
                "labels": labels,
                "data": data
            }
    

    def get_avg_task_time(self, user):
        user_projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True),
            is_active=True
        )

        avg_task_time = (
            Task.objects.filter(project__in=user_projects, is_active=True)
            .values('project__name')
            .annotate(avg_time=Avg('hours_count'))
            .order_by('-avg_time')
        )

        top_projects = avg_task_time[:3]

        avg_task_time_data = {
            "labels": [entry['project__name'] for entry in top_projects],
            "data": [round(entry['avg_time'], 2) for entry in top_projects],
        }

        return avg_task_time_data

    def get_cost_by_project(self, user):
        user_projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True),
            is_active=True
        )

        project_costs = (
            Task.objects.filter(project__in=user_projects, is_active=True)
            .values('project__name')
            .annotate(total_cost=Sum('total_price'))
            .order_by('-total_cost')
        )

        top_projects = project_costs[:3]

        cost_by_project_data = {
            "labels": [entry['project__name'] for entry in top_projects],
            "data": [float(entry['total_cost']) if isinstance(entry['total_cost'], Decimal) else entry['total_cost'] for entry in top_projects],
        }

        return cost_by_project_data
    

    def get_task_distribution(self, user):
        user_projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True),
            is_active=True
        )

        project_task_counts = (
            Task.objects.filter(project__in=user_projects, is_active=True)
            .values('project__name')
            .annotate(task_count=Count('id'))
            .order_by('-task_count')
        )

        top_projects = project_task_counts[:3]

        task_distribution_data = {
            "labels": [entry['project__name'] for entry in top_projects],
            "data": [entry['task_count'] for entry in top_projects],
        }

        return task_distribution_data
    
    def get_hours_by_project(self, user):
        user_projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True),
            is_active=True
        )

        project_hours = (
            Task.objects.filter(project__in=user_projects, is_active=True)
            .values('project__name')
            .annotate(total_hours=Sum('hours_count'))
            .order_by('-total_hours')
        )

        top_projects = project_hours[:3]

        hours_by_project_data = {
            "labels": [entry['project__name'] for entry in top_projects],
            "data": [entry['total_hours'] for entry in top_projects],
        }

        return hours_by_project_data

    
    def get_chart_data(self, user):

        return {
            "tasksByDay": self.get_task_per_day(user),
            "avgTaskTime": self.get_avg_task_time(user),
            "costByProject": self.get_cost_by_project(user),
            "taskDistribution": self.get_task_distribution(user),
            "hoursByProject": self.get_hours_by_project(user),
        }


    def get_data(self, request):
        context = super().get_data(request)
        chart_data = self.get_chart_data(self.request.user)

        context.update({
            'page_name': self.page_name,
            'active_page': self.active_page,
            'project_list': self.get_projects(self.request.user),
            'chart_data': chart_data,
        })
        
        return context


class ProjectsListView(BasicDataView):
    template_name = "project/projects.html"
    page_name = "Projects"
    active_page = "Projects"

    def get_projects(self, user):
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True),
            is_active=True
        ).distinct().order_by('-updated_at')

        projects_list = list()
        counter = 0
        for project in projects:
            counter += 1

            task_count = Task.objects.filter(project=project, is_active=True).count()
            total_sum = Task.objects.filter(project=project, is_active=True).aggregate(
                total=Sum('total_price')
            )['total'] or 0

            project_url = reverse('project', kwargs={'pk': project.pk})
            projects_list.append([
                counter, 
                project.name[:32], 
                project.updated_at.strftime("%d %b %Y"), 
                f"$ {project.hourly_rate} per hour", 
                task_count, 
                f"$ {total_sum or 0:.2f}",
                project_url
            ])
        return projects_list
    
    def get_project_recent(self, user):
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True), 
            is_active=True
        ).distinct().order_by('-updated_at')[:6]

        projects_list = []
        for project in projects:
            task_count = Task.objects.filter(project=project, is_active=True).count()
            total_sum = Task.objects.filter(project=project, is_active=True).aggregate(
                total=Sum('total_price')
            )['total'] or 0

            project_data = {
                'task_count': task_count,
                'total_sum': total_sum,
                'project': project,
            }

            projects_list.append(project_data)
            

        return projects_list


    def get_data(self, request):
        context = super().get_data(request)

        context.update({
            'page_name': self.page_name,
            'active_page': self.active_page,
            'project_list': self.get_projects(self.request.user),
            'project_list_recent': self.get_project_recent(self.request.user)
        })
        
        return context


class CreateProject(View):
    anonimys = AnonymousUser()

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid() and request.user != self.anonimys:
            project = form.save(commit=False)
            project.owner = request.user
            project.save()

        referer_url = request.META.get('HTTP_REFERER')

        if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
            return HttpResponseRedirect(referer_url)
        else:
            return redirect('dashboard')


class ProjectDetailView(BasicDataView):
    template_name = "project/project_detail.html"
    active_page = "Projects"

    def get_tasks(self, user, project):
        tasks = Task.objects.filter(project=project, assigned_to=user, is_active=True).order_by('-updated_at')
        tasks_list = list()
        counter = 0
        for task in tasks:
            counter += 1
            task_url = reverse('delete_task', kwargs={'project_id': project.id, 'task_id': task.id})
            tasks_list.append([
                counter, 
                task.name[:16],
                task.description[:32],
                task.assigned_to.username,
                task.date_for.strftime("%d %b %Y"), 
                f'{task.hours_count} h', 
                f"$ {task.total_price}",
                task_url
            ])
        return tasks_list
    
    def project_members(self, project):
        members = TeamMember.objects.filter(project=project, is_active=True)
        return members
    
    def get_data(self, request, pk):
        context = super().get_data(request)
        projects = Project.objects.filter(id=pk)
        if not len(projects):
            raise Http404("Page not found")
        
        project = projects[0]


        context.update({
            'page_name': project.name,
            'active_page': self.active_page,
            'task_list': self.get_tasks(self.request.user, project),
            'project': project,
            'project_members': self.project_members(project)
        })
        
        return context


class CreateTask(View):
    anonimys = AnonymousUser()

    def post(self, request, project_id):
        form = TaskForm(request.POST)
        if form.is_valid() and request.user != self.anonimys:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return HttpResponseNotFound("Project not found")

            task = form.save(commit=False)
            task.assigned_to = request.user
            task.project = project
            task.status = 'pending'

            if not task.date_for:
                task.date_for = datetime.now()
            
            task.save()

        referer_url = request.META.get('HTTP_REFERER')

        if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
            return HttpResponseRedirect(referer_url)
        else:
            return redirect('dashboard')


class EditProjectView(View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        data = {
            "name": project.name,
            "hourly_rate": project.hourly_rate,
            "description": project.description,
        }
        return JsonResponse(data)

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        form = ProjectForm(request.POST, instance=project)
        
        if form.is_valid():
            if request.user == project.owner:
                form.save() 
                
            referer_url = request.META.get('HTTP_REFERER')

            if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
                return HttpResponseRedirect(referer_url)
            else:
                return redirect('dashboard')


class AddTeamMemberView(View):
    anonimys = AnonymousUser()

    def return_back(self, request):
        referer_url = request.META.get('HTTP_REFERER')

        if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
            return HttpResponseRedirect(referer_url)
        else:
            return redirect('dashboard')

    def post(self, request, project_id):
        form = AddTeamMemberForm(request.POST)
        project = get_object_or_404(Project, id=project_id)
        
        if request.user == project.owner:

            if form.is_valid() and request.user != self.anonimys:
                username = form.cleaned_data['username']
                status = 'editor'

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return self.return_back(request)
                
                team_member = TeamMember.objects.filter(user=user, project=project).first()
                print(team_member)
                if team_member:
                    team_member.is_active = True
                    team_member.save()
                    print('alex')
                else:
                    TeamMember.objects.create(user=user, project=project, status=status)

        return self.return_back(request)


class RemoveMemberView(View):
    anonimys = AnonymousUser()

    def post(self, request, project_id, member_id):
        project = get_object_or_404(Project, id=project_id)
        member = get_object_or_404(TeamMember, id=member_id, project=project)
        
        if request.user == project.owner:
            member.is_active = False
            member.save()

        referer_url = request.META.get('HTTP_REFERER')

        if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
            return HttpResponseRedirect(referer_url)
        else:
            return redirect('dashboard')
        

class ProjectActivityView(BasicDataView):
    template_name = "project/activity.html"
    page_name = "Activity"
    active_page = "Activity"

    def get_activities(self, project):
        activities = Activity.objects.filter(project=project).order_by('-timestamp')
        activities_list = list()
        counter = 0
        for activity in activities:
            counter += 1
            activities_list.append([
                counter, 
                activity.action,
                activity.details,
                activity.timestamp.strftime("%d %b %Y"), 
                activity.user.username,
            ])
        return activities_list
    
    def get_projects(self, user):
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True),
            is_active=True
        ).distinct().order_by('-updated_at')
        return projects
    
    def get_data(self, request, project_id):
        context = super().get_data(request)
        projects = Project.objects.filter(id=project_id)
        if not len(projects):
            raise Http404("Page not found")
        
        project = projects[0]

        context.update({
            'page_name': self.page_name,
            'active_page': self.active_page,
            'activities_list': self.get_activities(project),
            'project': project,
            'projects': self.get_projects(self.request.user)
        })
        
        return context
    

class ActivityView(BasicDataView):
    anonimys = AnonymousUser()

    def get(self, request):
        if request.user == self.anonimys:
            return redirect('login')
        
        projects = Project.objects.filter(
            Q(owner=request.user) | Q(team_members__user=request.user, team_members__is_active=True)
        ).distinct().order_by('-updated_at')

        if not projects.exists():
            return redirect('dashboard')
        
        referer_url = request.META.get('HTTP_REFERER', None)

        if referer_url:
            parsed_url = urlparse(referer_url)
            path_parts = parsed_url.path.strip('/').split('/')
            if 'project' in path_parts and path_parts.index('project') + 1 < len(path_parts):
                try:
                    project_id = int(path_parts[path_parts.index('project') + 1])
                    if Project.objects.filter(id=project_id, is_active=True).exists():
                        return redirect('project_activity', project_id=project_id)
                except ValueError:
                    pass  

        first_project = projects.first()
        return redirect('project_activity', project_id=first_project.id)


class ProjectReportView(BasicDataView):
    template_name = "project/Report.html"
    page_name = "Reports"
    active_page = "Reports"
    
    def get_projects(self, user):
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members__user=user, team_members__is_active=True),
            is_active=True
        ).distinct().order_by('-updated_at')
        return projects
    
    def get_task_list(self, project, start_date=None, end_date=None, assigned_to=None):
        tasks = Task.objects.filter(project=project, is_active=True)
        
        if assigned_to:
            tasks = tasks.filter(assigned_to__id=assigned_to)
        
        if start_date:
            tasks = tasks.filter(date_for__gte=start_date)
        
        if end_date:
            tasks = tasks.filter(date_for__lte=end_date)

        tasks = tasks.order_by('-date_for')

        tasks_list = list()
        counter = 0
        for task in tasks:
            counter += 1
            tasks_list.append([
                counter, 
                task.name,
                task.description,
                task.assigned_to.username if task.assigned_to else "Unassigned",
                task.date_for.strftime("%d %b %Y") if task.date_for else "No date",
                task.hours_count,
                str(task.total_price)
            ])
        return tasks_list

    def get_amount_summary(self, tasks):
    # Считаем сумму только для переданных задач
        total_amount = tasks.aggregate(total=Sum('total_price'))['total'] or 0
        return float(total_amount)  # Преобразуем в float для передачи в JSON

    def filter_tasks(self, project, start_date=None, end_date=None, assigned_to=None):
        tasks = Task.objects.filter(project=project, is_active=True)

        if assigned_to:
            tasks = tasks.filter(assigned_to__id=assigned_to)
        
        if start_date:
            tasks = tasks.filter(date_for__gte=start_date)
        
        if end_date:
            tasks = tasks.filter(date_for__lte=end_date)

        return tasks
    
    def get_workload_by_day(self, tasks):
        # Временная нагрузка по дням
        tasks_by_day = (
            tasks.values('date_for')
            .annotate(hours_worked=Sum('hours_count'))
            .order_by('date_for')
        )
        workload_data = {
            "labels": [entry['date_for'].strftime('%Y-%m-%d') for entry in tasks_by_day if entry['date_for']],
            "data": [entry['hours_worked'] for entry in tasks_by_day if entry['date_for']],
        }
        return workload_data

    def get_time_distribution(self, tasks):
        # Распределение времени работы по участникам
        time_distribution = (
            tasks.values('assigned_to__username')
            .annotate(total_hours=Sum('hours_count'))
            .order_by('-total_hours')
        )
        distribution_data = {
            "labels": [entry['assigned_to__username'] or "Unassigned" for entry in time_distribution],
            "data": [entry['total_hours'] for entry in time_distribution],
        }
        return distribution_data

    def get_payment_by_employee(self, tasks):
        # Оплата каждому сотруднику
        payment_data = (
            tasks.filter(is_billable=True)
            .values('assigned_to__username')
            .annotate(total_payment=Sum('total_price'))
            .order_by('-total_payment')
        )
        payment_chart_data = {
            "labels": [entry['assigned_to__username'] or "Unassigned" for entry in payment_data],
            "data": [float(entry['total_payment'] or 0) for entry in payment_data],
        }
        return payment_chart_data

    
    def get_data(self, request, project_id):
        context = super().get_data(request)
        projects = Project.objects.filter(id=project_id)
        if not len(projects):
            raise Http404("Page not found")
        
        project = projects[0]

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        assigned_to = request.GET.get('assign_to')

        tasks = self.filter_tasks(project, start_date=start_date, end_date=end_date, assigned_to=assigned_to)

        context.update({
            'page_name': self.page_name,
            'active_page': self.active_page,
            'project': project,
            'projects': self.get_projects(self.request.user),
            'task_list': self.get_task_list(project, start_date=start_date, end_date=end_date, assigned_to=assigned_to),
            'amount_summary': self.get_amount_summary(tasks),
            'chart_data': {
                'workloadByDay': self.get_workload_by_day(tasks),
                'timeDistribution': self.get_time_distribution(tasks),
                'paymentByEmployee': self.get_payment_by_employee(tasks)
            }
        })
        
        return context


class ReportView(BasicDataView):
    anonimys = AnonymousUser()

    def get(self, request):
        if request.user == self.anonimys:
            return redirect('login')
        
        projects = Project.objects.filter(
            Q(owner=request.user) | Q(team_members__user=request.user, team_members__is_active=True)
        ).distinct().order_by('-updated_at')

        if not projects.exists():
            return redirect('dashboard')
        
        referer_url = request.META.get('HTTP_REFERER', None)

        if referer_url:
            parsed_url = urlparse(referer_url)
            path_parts = parsed_url.path.strip('/').split('/')
            if 'project' in path_parts and path_parts.index('project') + 1 < len(path_parts):
                try:
                    project_id = int(path_parts[path_parts.index('project') + 1])
                    if Project.objects.filter(id=project_id, is_active=True).exists():
                        return redirect('project_report', project_id=project_id)
                except ValueError:
                    pass

        first_project = projects.first()
        return redirect('project_report', project_id=first_project.id)
    

class DeleteTaskView(View):
    anonimys = AnonymousUser()

    def post(self, request, project_id, task_id):
        project = get_object_or_404(Project, id=project_id)
        task = get_object_or_404(Task, id=task_id, project=project)

        # Проверка прав на удаление задачи
        if not (request.user == project.owner or 
                project.team_members.filter(user=request.user, is_active=True).exists()):
            
            referer_url = request.META.get('HTTP_REFERER')
            if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
                return HttpResponseRedirect(referer_url)
            else:
                return redirect('dashboard')

        task.delete()

        referer_url = request.META.get('HTTP_REFERER')
        if referer_url and referer_url.startswith(request.build_absolute_uri('/')[:-1]):
            return HttpResponseRedirect(referer_url)
        else:
            return redirect('dashboard')