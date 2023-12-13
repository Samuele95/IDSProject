from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, Shop, FidelityProgram, Catalogue, Product, Transaction
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
        validate_password = make_password

class ShopSerializer(serializers.HyperlinkedModelSerializer):
    """
    Shop serialization class for field validation purposes.
    """

    class Meta:
        model = Shop
        fields = ['url', 'name', 'email', 'phone',
                  'location', 'owner', 'employees']
        extra_kwargs = {'employees': {'required': False}}

class FidelityProgramSerializer(serializers.HyperlinkedModelSerializer):
    """
    Fidelity program serialization class for field validation purposes.
    """

    points_coefficient = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5

    )

    prize_coefficient = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5
    )

    class Meta:
        model = FidelityProgram
        fields = ['url', 'name', 'program_type', 'description',
                  'points_coefficient', 'prize_coefficient',
                  'shop_list']
        extra_kwargs = {'shop_list': {'required': False}}


class PointsProgramSerializer(FidelityProgramSerializer):
    """
    POINTS type Fidelity program serialization class for field validation purposes.
    """
    program_type = serializers.CharField(
        default=serializers.CreateOnlyDefault(FidelityProgram.POINTS),
        validators=[
            RegexValidator(
                regex=FidelityProgram.POINTS,
                message="Fidelity program type must be POINTS"
            )
        ]
    )


class LevelsProgramSerializer(FidelityProgramSerializer):
    """
    LEVELS type Fidelity program serialization class for field validation purposes.
    """
    points_coefficient = serializers.FloatField(
        validators=[MinValueValidator(0.000), MaxValueValidator(0.010)],
        default=0.005

    )

    prize_coefficient = serializers.FloatField(
        validators=[MinValueValidator(0.000), MaxValueValidator(0.010)],
        default=0.005
    )

    program_type = serializers.CharField(
        default=serializers.CreateOnlyDefault(FidelityProgram.LEVELS),
        validators=[
            RegexValidator(
                regex=FidelityProgram.LEVELS,
                message="Fidelity program type must be LEVELS"
            )
        ]

    )


class CashbackProgramSerializer(FidelityProgramSerializer):
    """
    CASHBACK type Fidelity program serialization class for field validation purposes.
    """
    points_coefficient = serializers.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(0.0)],
        default=-0.5
    )

    prize_coefficient = serializers.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        default=-0.5
    )

    program_type = serializers.CharField(
        default=serializers.CreateOnlyDefault(FidelityProgram.CASHBACK),
        validators=[
            RegexValidator(
                regex=FidelityProgram.CASHBACK,
                message="Fidelity program type must be CASHBACK"
            )
        ]
    )


class MembershipProgramSerializer(FidelityProgramSerializer):
    """
    MEMBERSHIP type Fidelity program serialization class for field validation purposes.
    """
    points_coefficient = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(0.0)],
        default=0.0
    )

    prize_coefficient = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(0.0)],
        default=0.0
    )

    program_type = serializers.CharField(
        default=serializers.CreateOnlyDefault(FidelityProgram.MEMBERSHIP),
        validators=[
            RegexValidator(
                regex=FidelityProgram.MEMBERSHIP,
                message="Fidelity program type must be MEMBERSHIP"
            )
        ]
    )


class CatalogueSerializer(serializers.HyperlinkedModelSerializer):
    """
    Catalogue elements serialization class for field validation purposes.
    """

    class Meta:
        model = Catalogue
        fields = ['url', 'id', 'points',
                  'customer', 'fidelity_program']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    """
    Product serialization class for field validation purposes.
    """

    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'value',
                  'points_coefficient', 'prize_coefficient', 'is_persistent',
                  'shop', 'fidelity_program', 'owning_users']
        extra_kwargs = {
            'fidelity_program': {'required': False},
            'owning_users': {'required': False}
        }


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Transaction serialization class for field validation purposes.
    """

    class Meta:
        model = Transaction
        fields = ['url', 'id', 'executed_at',
                  'user', 'shop', 'shopping_cart',
                  'total']
        #extra_kwargs = {'shopping_cart': {'required': False}}

    def create(self, validated_data):
        transaction = Transaction(
            user=validated_data['user'],
            shop=validated_data['shop'],
        )
        for prod in validated_data['shopping_cart']:
            transaction.shopping_cart.add(prod)
        transaction.save()
        return transaction
