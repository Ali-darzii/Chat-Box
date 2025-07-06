from django.utils import timezone
from django.db import models

from auth_module.models import User

class GroupBox(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, related_name='users_group')
    admins = models.ManyToManyField(User, related_name='admins_group')
    last_message = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-last_message",)

class GroupBoxMessage(models.Model):
    message = models.TextField(blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to="gp_files/")
    group = models.ForeignKey(GroupBox, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, related_name="group_sender", on_delete=models.CASCADE)
    is_delete = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender}: {self.group.name}"

    class Meta:
        ordering = ("-created_at",)


class GroupBoxAvatar(models.Model):
    group = models.ForeignKey(GroupBox, on_delete=models.CASCADE, related_name="group_avatars")
    avatar = models.ImageField(upload_to="gp_avatars/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)