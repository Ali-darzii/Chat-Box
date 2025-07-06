from django.urls import path
from group_module.api import group

urlpatterns = [
    path("create/", group.CreateGroupBox.as_view(), name="create_group_box"),
    path("<int:pk>/detail/", group.DetailGroupBox.as_view(), name="detail_group_box"),
    path("<int:pk>/edit/", group.EditGroupBoxName.as_view(), name="edit_group_box_name"),
]
