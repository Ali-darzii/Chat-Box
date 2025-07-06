from django.urls import path
from rest_framework.routers import DefaultRouter

from group_module.api import group

router = DefaultRouter()
router.register(r"group/avatar", group.GroupBoxAvatarViewSet, basename="group_avatar")




urlpatterns = [
    path("create/", group.CreateGroupBox.as_view(), name="create_group_box"),
    path("<int:pk>/detail/", group.DetailGroupBox.as_view(), name="detail_group_box"),
    path("<int:pk>/name/edit/", group.EditGroupBoxName.as_view(), name="edit_group_box_name"),
    path("<int:pk>/users/edit/", group.EditGroupBoxUsers.as_view(), name="edit_group_box_users"),
    path("<int:pk>/admins/edit/", group.EditGroupBoxAdmins.as_view(), name="edit_group_box_admins"),
] + router.urls
