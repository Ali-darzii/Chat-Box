from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView
from django.db.models import Q

from private_module.serializers import PrivateBoxSerializer
from private_module.models import PrivateBox

class GetPrivateBox(ListAPIView):
    """
    List of users are in the same Box
    but authenticated user is excluded
    # TODO:user field from id need to be full information
    
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = PrivateBoxSerializer

    def get_queryset(self):
        return PrivateBox.objects.filter(
            Q(first_user=self.request.user) |Q(second=self.request.user)
        )
    
    
    

class CreatePrivatBox(CreateAPIView):
    """ 
    
    We will use this if it's first message.
    Then we call SendPrivateMessage EndPoint.
    
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = PrivateBoxSerializer
    



