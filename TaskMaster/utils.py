from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, UserActivity
import pandas as pd
import matplotlib as mtplot


def send_email_notification_task(user, task):
    for user_assigned in task.assigned_to.all():
        subject = f'New Task: {task.task_name}'
        message = f'Hi, {user.first_name} {user.last_name} just set up a new task for you!\nCheck it out at http://127.0.0.1:8000/taskmaster/'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user_assigned.email, ]
        # send_mail(subject, message, email_from, recipient_list)

        # Create a notification for the user_assigned
        notification = Notification.objects.create(
            user=user_assigned,
            task=task,
            message=f'New Task: {task.task_name}',
        )

        track_user_activity(user, 'Send email and notification', f'{user.first_name} {user.last_name} send email and notification to {user_assigned.first_name} {user_assigned.last_name}')


def track_user_activity(user, action, action_elaborate):
    UserActivity.objects.create(
        user=user,
        action=action,
        action_elaborated=action_elaborate)


def analysis(user):
    user_activity_data = UserActivity.objects.filter(user=user, action='Login').order_by('-timestamp')
    count_login = len(user_activity_data)
    user_activity_data_df = pd.DataFrame(list(user_activity_data))

    # print(count_login)
    # print(user_activity_data_df.count())
