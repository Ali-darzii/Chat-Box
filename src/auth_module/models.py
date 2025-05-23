from django.contrib.auth.models import AbstractUser
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    """
    Custom user manager for our project is base on phone_no.
    We MUST not use functionality of this class in codes.
    We just do it for manager.py createsuperuser to works.
    """

    def create_user(self, phone_no, password, **extra_fields):
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        user = self.model(phone_no=phone_no, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_no, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone_no, password, **extra_fields)


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=150, unique=True, validators=[username_validator],
                                error_messages={
                                    "unique": _("A user with that username already exists."),
                                },
                                blank=True,
                                null=True
                                )
    phone_no = models.CharField(max_length=11, unique=True, db_index=True)
    avatar = models.ImageField(null=True, blank=True, upload_to="media/images/avatars/")

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = []


class Profile(models.Model):
    # TODO: implant later
    pass
