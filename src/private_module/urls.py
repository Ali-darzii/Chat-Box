from django.urls import path
from private_module import views

urlpatterns = [
    path("list/", views.GetPrivateBox.as_view(), name="list_private"),
    path("create/", views.CreatePrivatBox.as_view(), name="create_private"),
]
