from rest_framework import serializers
from .models import User, Shop, FidelityProgram, Catalogue
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

