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
    message = models.TextField()
    file = models.FileField(upload_to="pv_files/")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    box = models.ForeignKey(PrivateBox, on_delete=models.CASCADE, related_name="box")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
