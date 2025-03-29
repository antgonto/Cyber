# app/api/models.py
from django.db import models
from django.contrib.auth.hashers import make_password


class User(models.Model):
    USER_ROLES = (
        ('admin', 'Administrator'),
        ('analyst', 'Security Analyst'),
        ('manager', 'Security Manager'),
        ('user', 'Regular User'),
    )

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=50, choices=USER_ROLES, default='user')
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Hash password if it has been changed
        if self._state.adding or (
            not self._state.adding and
            User.objects.get(pk=self.pk).password != self.password
        ):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username