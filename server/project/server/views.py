from rest_framework import viewsets
from .models import User, Shop
from .modelvalidators import UserSerializer, ShopSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint allowing users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class ShopViewSet(viewsets.ModelViewSet):
    """
    API endpoint allowing shops to be viewed or edited.
    """
    queryset = Shop.objects.all().order_by('name')
    serializer_class = ShopSerializer