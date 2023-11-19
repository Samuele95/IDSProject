from rest_framework import serializers
from .models import User, Shop
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    User serialization class for field validation purposes.
    """

    class Meta:
        model = User
        fields = ['url', 'username', 'password', 'email',
                  'groups', 'phone', 'avatar', 'bio',
                  'location']


class ShopSerializer(serializers.HyperlinkedModelSerializer):
    """
    Shop serialization class for field validation purposes.
    """

    class Meta:
        model = Shop
        fields = ['url', 'name', 'email', 'phone',
                  'location', 'owner', 'employees']
        extra_kwargs = {'employees': {'required': False}}

