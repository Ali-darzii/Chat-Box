from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from group_module.models import GroupBox, GroupBoxAvatar
from utils.response import ErrorResponses as error
from private_module.serializers import ChatUserSerializer


class GroupAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBoxAvatar
        fields = "__all__"


class CreateGroupBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBox
        fields = "__all__"

    avatar = serializers.ImageField(required=False, write_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

    def get_avatar_url(self, obj):
        group_avatar = obj.group_avatars.last()
        return group_avatar.avatar.url if group_avatar else None

    def validate(self, attrs):
        user = self.context["request"].user
        users = attrs.get("users")
        admins = attrs.get("admins")

        if len(users) < 2:
            raise serializers.ValidationError(error.BAD_REQUEST)
        if user not in users or user not in admins:
            raise serializers.ValidationError(error.BAD_REQUEST)
        return attrs

    def create(self, validated_data):
        avatar = validated_data.pop("avatar", None)
        group = super().create(validated_data)
        if avatar:
            GroupBoxAvatar.objects.create(group=group, avatar=avatar)
        return group


class DetailGroupBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBox
        fields = "__all__"

    users = ChatUserSerializer(many=True)
    avatars = serializers.SerializerMethodField()

    def get_avatars(self, obj):
        serializer = GroupAvatarSerializer(obj.group_avatars.all(), many=True)
        return serializer.data


class EditGroupBoxNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBox
        fields = ("name",)


class EditGroupBoxAdminsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBox
        fields = ("admins",)

    def validate(self, attrs):
        if "admins" not in attrs:
            raise serializers.ValidationError(error.BAD_FORMAT)
        return attrs

    def update(self, instance, validated_data):
        request_user = self.context["request"].user
        new_admins = set(validated_data["admins"])
        current_admins = set(instance.admins.all())
        group_users = set(instance.users.all())

        if not new_admins.issubset(group_users):
            raise serializers.ValidationError("All admins must be members of the group.")

        removed_admins = current_admins - new_admins
        if removed_admins - {request_user}:
            raise serializers.ValidationError("You cannot remove other admins.")

        added_admins = new_admins - current_admins
        for added_user in added_admins:
            if added_user not in group_users:
                raise serializers.ValidationError("You can only add users who are already in the group.")

        instance.admins.set(new_admins)
        instance.save()
        return instance



class EditGroubBoxUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBox
        fields = ("users",)

    def validate(self, attrs):
        if "users" not in attrs:
            raise serializers.ValidationError(error.BAD_FORMAT)
        return attrs

    def update(self, instance, validated_data):
        new_users = validated_data["users"]
        current_admins = instance.admins.all()

        for admin in current_admins:
            if admin not in new_users:
                instance.admins.remove(admin)

        return super().update(instance, validated_data)


class GroupBoxAvatarViewSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBoxAvatar
        fields = "__all__"
        extra_kwargs = {"created_at": {"read_only": True}}
