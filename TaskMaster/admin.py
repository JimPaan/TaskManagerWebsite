from django.contrib import admin
from .models import CustomUser, Task, Notification, UserActivity


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
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__email', 'action')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
