from django.urls import path
from private_module import views

urlpatterns = [
    path("create-private/", views.CreatePrivateMessageView.as_view(), name="create_private"),
]
