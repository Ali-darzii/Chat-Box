from django.db import models
from auth_module.models import User

class UserAvatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avatars")
    avatar = models.ImageField(null=True, blank=True, upload_to="avatars/")
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

