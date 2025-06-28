from django.urls import path
from group_module.api import group

urlpatterns = [
    path("create/", group.CreateGroupBox.as_view(), name="create_group_box"),

]