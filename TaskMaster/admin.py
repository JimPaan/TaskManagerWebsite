from django.contrib import admin
from .models import CustomUser, Task, Notification, UserActivity, Project


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'assigned_by', 'deadline')
    list_filter = ('assigned_by', 'deadline')
    search_fields = ('task_name', 'assigned_by__email', 'assigned_to__email')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('user__email', 'message')


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'action_elaborated', 'timestamp')
    search_fields = ('user__email', 'action')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'created_by', 'is_done', 'finish']
    list_filter = ['is_done', 'created_by']
    search_fields = ['name', 'created_by__username']
    date_hierarchy = 'start_date'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
admin.site.register(Project, ProjectAdmin)
