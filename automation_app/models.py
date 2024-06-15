# automation_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('order_processing', 'Order Processing'),
        ('invoice_processing', 'Invoice Processing'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='automation_app_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='automation_app_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class AutomationType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Automation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    automation_type = models.ForeignKey(AutomationType, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserAutomation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE)


class JobResult(models.Model):
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.TextField()
    satisfied = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)


class AutomationLog(models.Model):
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    execution_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    log_details = models.TextField()

    def __str__(self):
        return f"Log for {self.automation.name} by {self.user.username} at {self.execution_time}"
