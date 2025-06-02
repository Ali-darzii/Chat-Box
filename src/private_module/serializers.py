from rest_framework import serializers
from django.db import IntegrityError as UniqueError
from django.db.models import Q
from utils.response import ErrorResponses as error
from private_module.models import PrivateBox


class GetUsersByBoxSerializer(serializers.ModelSerializer):
    pass


class SendPrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateBox
        fields = ("room_id","receiver_id","first_user")
        extra_kwargs = {"first_user": {"read_only": True}}

    room_id = serializers.CharField(source="id", read_only=True)
    receiver_id = serializers.IntegerField(source="second_user_id", min_value=1)

    def create(self, validated_data):
        auth_user = self.context["request"].user
        other_user_id = validated_data["second_user_id"]

        if auth_user.id == other_user_id:
            raise serializers.ValidationError(error.BAD_FORMAT)
        box = PrivateBox.objects.filter(
            Q(first_user=auth_user, second_user_id=other_user_id) |
            Q(first_user_id=other_user_id, second_user=auth_user)
        ).first()

        if box:
            return box
        return PrivateBox.objects.create(first_user=auth_user, second_user_id=other_user_id)