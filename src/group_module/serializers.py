from rest_framework import serializers

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



class GroupBoxDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBox
        fields = "__all__"

    users = ChatUserSerializer(many=True)
    avatars = serializers.SerializerMethodField()

    def get_avatars(self, obj):
        serializer = GroupAvatarSerializer(obj.group_avatars.all(), many=True)
        return serializer.data
