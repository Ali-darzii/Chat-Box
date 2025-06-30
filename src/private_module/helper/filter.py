import django_filters
from private_module.models import PrivateMessage

class PrivateMessageFilter(django_filters.FilterSet):
    class Meta:
        model = PrivateMessage
        fields = ["start", "end"]

    start = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    end = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")