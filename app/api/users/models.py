from django.contrib.auth.hashers import make_password
from django.db import models


class User(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = "admin", "Administrator"
        ANALYST = "analyst", "Security Analyst"
        MANAGER = "manager", "Security Manager"
        USER = "user", "Regular User"

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=50, choices=RoleChoices.choices, default=RoleChoices.USER)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Hash password if it has been changed
        if self._state.adding or (
            not self._state.adding and
            User.objects.filter(pk=self.pk).exists() and
            User.objects.get(pk=self.pk).password != self.password
        ):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

class UserActivityLog(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'user_activity_logs'
        verbose_name = "User Activity Log"
        verbose_name_plural = "User Activity Logs"
        indexes = [
            models.Index(fields=['user_id'], name='idx_ual_user_id'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"