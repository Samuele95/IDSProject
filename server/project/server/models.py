from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Basic User class used by this application.
    It enhances the default user type adding an avatar,
    a biography and a location info.
    """

    # Define inherited username field as primary key
    AbstractUser._meta.get_field('username').primary_key = True

    phone = models.CharField(max_length=13)
    avatar = models.ImageField(
        upload_to='users/avatars/%Y/%m/%d',
        default='users/avatars/default.jpg'
    )
    bio = models.TextField(max_length=500, null=True)
    location = models.CharField(max_length=30, null=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = '1. Users'

    def __str__(self):
        return self.username


class Shop(models.Model):
    """
    Shop model element, defined through a 
    name, an email address, a phone number
    and a textual address. Two Shop instances
    cannot have the same name and/or email.

    It is owned by a User and several
    other User elements may be associated
    to it as employees
    """
    name = models.CharField(max_length=30, primary_key=True)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=13)
    location = models.CharField(max_length=30, null=True)

    # Model relationships
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='shop_owner')
    employees = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = 'shop'
        verbose_name_plural = '2. Shops'

    def __str__(self):
        return self.name

class FidelityProgram(models.Model):
    CASHBACK = 'CASHBACK'
    LEVELS = 'LEVELS'
    POINTS = 'POINTS'
    MEMBERSHIP = 'MEMBERSHIP'
    GENERIC = 'GENERIC'
    PROGRAM_TYPE_CHOICES = [
        (CASHBACK, "Cashback"),
        (LEVELS, "Levels"),
        (POINTS, "Points"),
        (MEMBERSHIP, "Membership"),
        (GENERIC, "Generic"),
    ]

    shop_list = models.ManyToManyField(Shop)
    name = models.CharField(max_length=30, primary_key=True)
    program_type = models.CharField(
        max_length=10,
        choices=PROGRAM_TYPE_CHOICES,
        default=GENERIC
    )
    description = models.TextField(max_length=1000)
    points_coefficient = models.FloatField()
    prize_coefficient = models.FloatField()

    class Meta:
        verbose_name = 'fidelityprogram'
        verbose_name_plural = '3. Fidelity Programs'

    def is_coalition(self):
        return self.shop_list.all().count() > 1

    def __str__(self):
        return '({name} , {prtype})'.format(name=self.name, prtype=self.program_type)


class Catalogue(models.Model):
    points = models.FloatField(null=True)

    # Database relationships
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='customer'
    )
    fidelity_program = models.ForeignKey(
        FidelityProgram,
        on_delete=models.SET_NULL,
        null=True,
        related_name='catalogue_fidelity_program'
    )

    class Meta:
        verbose_name = 'catalogue'
        verbose_name_plural = '4. Catalogue'
        constraints = [
            models.UniqueConstraint(fields=['customer', 'fidelity_program'], name='catalogue_key')
        ]

    def __str__(self):
        return '({program}, {csmr}, {pts})'.format(
            program=self.fidelity_program,
            csmr=self.customer,
            pts=self.points
        )

