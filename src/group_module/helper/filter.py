import django_filters

from group_module.models import GroupBoxAvatar

class GroupBoxAvatarFilter(django_filters.FilterSet):
    class Meta:
        model = GroupBoxAvatar
        fields = ["group_id"]
    group_id = django_filters.NumberFilter(field_name="group_id", required=True)