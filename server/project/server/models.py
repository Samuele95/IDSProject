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
