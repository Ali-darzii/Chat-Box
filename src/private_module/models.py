from django.db import models

from django.utils import timezone
from reactivex.operators import first

from auth_module.models import User


class PrivateBox(models.Model):
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="first_user")
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="second_user")
    last_message = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_user} - {self.second_user}"

    class Meta:
        unique_together = ("first_user", "second_user")
        ordering = ("-last_message",)

    def receiver(self, sender: User):
        return self.second_user if self.first_user == sender else self.first_user

class PrivateMessage(models.Model):
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="pv_files/", blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    box = models.ForeignKey(PrivateBox, on_delete=models.CASCADE, related_name="box")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} - {self.box}"

    class Meta:
        ordering = ("-created_at",)
