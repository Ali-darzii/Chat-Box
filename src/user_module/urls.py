from django.urls import path
from rest_framework.routers import DefaultRouter

from user_module.api import user

router = DefaultRouter()

router.register("private/avatar", user.PrivateAvatarViewSet, basename="private_avatar")


urlpatterns = [
    path("private/edit/", user.PrivateEditUser.as_view(), name="edit_user"),
    path("public/<int:pk>/detail/", user.PublicUserDetail.as_view(), name="edit_user"),

] + router.urls