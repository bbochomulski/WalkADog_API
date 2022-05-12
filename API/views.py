from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from API.serializers import UserSerializer, WalkSerializer

from .models import Walk

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class WalksViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Walk.objects.all()
    serializer_class = WalkSerializer
    permission_classes = [permissions.IsAuthenticated]

