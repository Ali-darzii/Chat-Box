from django.db import models

from django.utils import timezone
from auth_module.models import User


class PrivateBox(models.Model):
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="first_user")
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="second_user")
    last_message = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("first_user", "second_user")
        ordering = ("-last_message",)

class PrivateMessage(models.Model):
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="pv_files/", blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    box = models.ForeignKey(PrivateBox, on_delete=models.CASCADE, related_name="box")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)