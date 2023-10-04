from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    position = models.CharField(max_length=30, default='Staff')
    division = models.CharField(max_length=30, default='Leadership')
    company = models.CharField(max_length=50, default='Visitor')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    collaborated_with = models.ManyToManyField(CustomUser, related_name='projects_collaborated_with')
    is_done = models.BooleanField(default=False)
    finish = models.DateTimeField(null=True, blank=True)

    @property
    def is_expired(self):
        return self.end_date <= timezone.now()

    def update_is_done(self):
        if self.task_set.filter(is_done=False).count() == 0:
            self.is_done = True
        else:
            self.is_done = False

        self.save()

    def __str__(self):
        return self.name


class Task(models.Model):
    task_name = models.CharField(max_length=100)
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_to = models.ManyToManyField(CustomUser, related_name='tasks_assigned_to')
    start = models.DateTimeField()
    deadline = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    is_done = models.BooleanField(default=False)
    finish = models.DateTimeField(null=True, blank=True)
    documents = models.FileField(upload_to='task_documents/', null=True, blank=True)
    types = models.CharField(max_length=50, default='Urgent and Important')

    @property
    def is_expired(self):
        return self.deadline <= timezone.now()

    def __str__(self):
        return self.task_name


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.message[:50]}"


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    action_elaborated = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}  {self.user.last_name}- {self.action} - {self.timestamp}"



