from django.db import models

from auth_module.models import User


class PrivateBox(models.Model):
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="first_user")
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="second_user")

    class Meta:
        unique_together = ("first_user", "second_user")