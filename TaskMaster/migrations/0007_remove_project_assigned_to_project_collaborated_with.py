# Generated by Django 4.2.5 on 2023-10-04 13:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TaskMaster', '0006_project_assigned_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='assigned_to',
        ),
        migrations.AddField(
            model_name='project',
            name='collaborated_with',
            field=models.ManyToManyField(related_name='projects_collaborated_with', to=settings.AUTH_USER_MODEL),
        ),
    ]
