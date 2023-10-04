from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, TaskForm, UpdateProfileForm, ProjectForm
from django.contrib import messages
from .models import CustomUser, Task, Notification, Project
from .utils import send_email_notification_task, track_user_activity, analysis
from django.core.files.storage import default_storage
import os
from django.conf import settings
from datetime import datetime
from django.http import HttpResponse, Http404


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                track_user_activity(user, 'Login', 'Login into the website')
            else:
                print("user is not authenticated")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    if messages.get_messages(request):
        messages_list = [str(message) for message in messages.get_messages(request)]
        return render(request, 'login.html', {'form': form, 'success_message': messages_list[0]})

    return render(request, 'login.html', {'form': form})


@login_required
def dashboard_view(request):
    track_user_activity(request.user, 'View dashboard', 'Viewing their dashboard')
    authorized = False
    authorize_position = [
        'CEO',
        'COO',
        'CFO',
        'CMO',
        'CIO',
        'CTO',
        'OM',
        'SM',
        'AM',
        'MM',
        'PM',
        'GM',
        'HRM',
        'PM',
        'CSR',
        'AE',
        'FM',
        'ED',
        'VP',
    ]

    for position in authorize_position:
        if request.user.position == position:
            authorized = True

    if authorized:
        users_in_same_company_division = CustomUser.objects.filter(company=request.user.company, division=request.user.division).exclude(id=request.user.id)
        tasks_incomplete = Task.objects.filter(assigned_by=request.user, is_done=False).exclude(id=request.user.id)
        tasks_complete = Task.objects.filter(assigned_by=request.user, is_done=True).exclude(id=request.user.id)
        projects = Project.objects.filter(created_by=request.user)
        analysis(request.user)
        context = {
            'users_in_same_company_division': users_in_same_company_division,
            'tasks_incomplete': tasks_incomplete,
            'tasks_complete': tasks_complete,
            'authorized': authorized,
            'projects': projects,
        }
        return render(request, 'dashboard.html', context)
    else:
        tasks_incomplete = Task.objects.filter(assigned_to=request.user.id, is_done=False).exclude(id=request.user.id)
        tasks_complete = Task.objects.filter(assigned_to=request.user.id, is_done=True).exclude(id=request.user.id)
        context = {
            'tasks_incomplete': tasks_incomplete,
            'tasks_complete': tasks_complete,
            'authorized': authorized,
        }
        return render(request, 'dashboard.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('index')


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            track_user_activity(user, 'Sign up', 'Signing up to the website')
            # Add a success message
            messages.success(request, 'The account has been registered. You can login now.')
            return redirect('login_view')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, current_user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            form.save_m2m()

            track_user_activity(request.user, 'Create task', f'Create Task: {task.task_name}')

            # Sending email to employees that were assigned after task was registered
            send_email_notification_task(request.user, task)
            return redirect('dashboard')
    else:
        form = TaskForm(current_user=request.user)
    return render(request, 'create_task.html', {'form': form})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, current_user=request.user)
        if form.is_valid():
            form.save()
            track_user_activity(request.user, 'Edit task', f'Edit task: {task.task_name}')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task, current_user=request.user)

    return render(request, 'edit_task.html', {'form': form, 'task': task})


@login_required
def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    track_user_activity(request.user, 'View details task', f'View details for task: {task.task_name}')

    authorized = False
    authorize_position = [
        'CEO',
        'COO',
        'CFO',
        'CMO',
        'CIO',
        'CTO',
        'OM',
        'SM',
        'AM',
        'MM',
        'PM',
        'GM',
        'HRM',
        'PM',
        'CSR',
        'AE',
        'FM',
        'ED',
        'VP',
    ]

    for position in authorize_position:
        if request.user.position == position:
            authorized = True

    if request.method == 'POST':
        if 'document' in request.FILES:
            document = request.FILES['document']

            # Check if the task already has a document, and delete it if it exists
            if task.documents:
                existing_file_path = os.path.join(settings.MEDIA_ROOT, str(task.documents))
                if default_storage.exists(existing_file_path):
                    default_storage.delete(existing_file_path)

            task.documents = document
            task.is_done = True
            task.finish = datetime.now()
            task.save()
            track_user_activity(request.user, 'Upload file', f'Upload file: {task.documents.name} to task: {task.task_name}')

    return render(request, 'task_details.html', {'task': task, 'authorized': authorized})


@login_required
def notifications_view(request):
    user_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
    track_user_activity(request.user, 'Open notification section', f'Opening their notifications section')
    return render(request, 'notifications.html', {'user_notifications': user_notifications})


@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    track_user_activity(request.user, 'Read notification', f'Read notification {notification.message}')
    return redirect('task_details', task_id=notification.task.id)


@login_required
def download_document(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if task.is_done and task.documents:
        track_user_activity(request.user, 'Download file', f'Download file: {task.documents.name}')
        document_path = task.documents.path
        with open(document_path, 'rb') as document_file:
            response = HttpResponse(document_file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{task.documents.name}"'
            return response
    else:
        raise Http404("Document not found")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.user == task.assigned_by:
        task.delete()
        messages.success(request, 'Task deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this task.')

    track_user_activity(request.user, 'Delete task', f'Delete task: {task.task_name}')
    return redirect('dashboard')


@login_required
def profile(request):
    users_in_same_company = CustomUser.objects.filter(company=request.user.company)
    track_user_activity(request.user, 'View profile page', 'View profile page')

    context = {
        'users_in_same_company': users_in_same_company,
    }
    return render(request, 'profile.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            track_user_activity(request.user, 'Update profile', 'Update profile')
            return redirect('profile')
    else:
        form = UpdateProfileForm(instance=request.user)

    context = {'form': form}
    return render(request, 'update_profile.html', context)


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, current_user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            track_user_activity(request.user, 'Create Project', f'Create Project: {project.name}')
            return redirect('dashboard')
    else:
        form = ProjectForm(current_user=request.user)

    return render(request, 'create_project.html', {'form': form})


@login_required
def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.task_set.all()

    # update the project
    project.update_is_done()

    tasks_completed = project.task_set.filter(is_done=True).count()
    tasks_count = project.task_set.all().count()

    authorized = False
    authorize_position = [
        'CEO',
        'COO',
        'CFO',
        'CMO',
        'CIO',
        'CTO',
        'OM',
        'SM',
        'AM',
        'MM',
        'PM',
        'GM',
        'HRM',
        'PM',
        'CSR',
        'AE',
        'FM',
        'ED',
        'VP',
    ]

    for position in authorize_position:
        if request.user.position == position:
            authorized = True

    context = {
        'project': project,
        'tasks': tasks,
        'authorized': authorized,
        'tasks_completed': tasks_completed,
        'tasks_count': tasks_count,
    }

    return render(request, 'project_details.html', context)
