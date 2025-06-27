from django.urls import path

from user_module.api import user

urlpatterns = [
    path("edit/", user.EditeUser.as_view(), name="edit_user"),
    path("<int:pk>/detail/", user.GetUserDetail.as_view(), name="edit_user"),

]