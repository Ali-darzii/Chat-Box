from django.contrib import admin
from auth_module import models


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(models.User, UserAdmin)