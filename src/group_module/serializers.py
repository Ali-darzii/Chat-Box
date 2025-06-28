from rest_framework import serializers

from group_module.models import GroupBox, GroupBox, GroupBoxAvatar
from utils.response import ErrorResponses as error


class GroupAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBoxAvatar
        exclude = ("group",)


class CreateGroupBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBox
        fields = ("name", "users", "admins", "avatar")

    avatar = serializers.ImageField(required=False)

    def validate(self, attrs):
        user = self.context['request'].user
        users = attrs.get('users')
        admins = attrs.get('admins')

        if len(users) < 2:
            raise serializers.ValidationError(error.BAD_REQUEST)
        if user not in users or user not in admins:
            raise serializers.ValidationError(error.BAD_REQUEST)
        return attrs

    def create(self, validated_data):
        avatar = validated_data.pop('avatar', None)
        group = super().create(validated_data)
        if avatar:
            GroupBoxAvatar.objects.create(group=group, avatar=avatar)
        return group
