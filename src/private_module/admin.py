from django.contrib import admin
from private_module import models

admin.site.register(models.PrivateBox)
@admin.register(models.PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "file", "sender", "box", "is_read", "is_delete")