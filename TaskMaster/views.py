from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, TaskForm, UpdateProfileForm
from django.contrib import messages
from .models import CustomUser, Task, Notification
from .utils import send_email_notification_task, track_user_activity
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
                track_user_activity(user, 'Login')
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
    track_user_activity(request.user, 'View dashboard')
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
        context = {
            'users_in_same_company_division': users_in_same_company_division,
            'tasks_incomplete': tasks_incomplete,
            'tasks_complete': tasks_complete,
            'authorized': authorized,
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
    track_user_activity(request.user, 'Logout')
    logout(request)
    return redirect('index')


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            track_user_activity(user, 'Sign up')
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

            track_user_activity(request.user, f'Create Task: {task.task_name}')

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
            track_user_activity(request.user, f'Edit task: {task.task_name}')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task, current_user=request.user)

    return render(request, 'edit_task.html', {'form': form, 'task': task})


@login_required
def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    track_user_activity(request.user, f'View details for task: {task.task_name}')

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
            track_user_activity(request.user, f'Upload file: {task.documents.name} to task: {task.task_name}')

    return render(request, 'task_details.html', {'task': task, 'authorized': authorized})


@login_required
def notifications_view(request):
    user_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
    track_user_activity(request.user, 'Open notification section')
    return render(request, 'notifications.html', {'user_notifications': user_notifications})


@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    track_user_activity(request.user, f'Read notification {notification.message}')
    return redirect('task_details', task_id=notification.task.id)


@login_required
def download_document(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if task.is_done and task.documents:
        track_user_activity(request.user, f'Download file: {task.documents.name}')
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

    track_user_activity(request.user, f'Delete task: {task.task_name}')
    return redirect('dashboard')


@login_required
def profile(request):
    users_in_same_company = CustomUser.objects.filter(company=request.user.company)
    track_user_activity(request.user, 'View profile page')

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
            track_user_activity(request.user, 'Update profile')
            return redirect('profile')  # Redirect to the profile page after updating
    else:
        form = UpdateProfileForm(instance=request.user)

    context = {'form': form}
    return render(request, 'update_profile.html', context)

