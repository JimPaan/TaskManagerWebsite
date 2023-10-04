from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login_view/', views.login_view, name='login_view'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('createproject/', views.create_project, name='create_project'),
    path('createtask/', views.create_task, name='create_task'),
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('task/<int:task_id>/', views.task_details, name='task_details'),
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('download_document/<int:task_id>/', views.download_document, name='download_document'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('project/<int:project_id>/', views.project_details, name='project_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
