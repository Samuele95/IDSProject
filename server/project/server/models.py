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
        default='users/avatars/default.jpg',
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
    points_coefficient = models.FloatField(default=0.5)
    prize_coefficient = models.FloatField(default=0.5)

    class Meta:
        verbose_name = 'fidelityprogram'
        verbose_name_plural = '3. Fidelity Programs'

    def is_coalition(self):
        return self.shop_list.all().count() > 1

    def __str__(self):
        return '({name} , {prtype})'.format(name=self.name, prtype=self.program_type)


class Catalogue(models.Model):
    points = models.FloatField(default=0.0)

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

    @classmethod
    def update_points(cls, customer, fprogram, offset):
        prev_points = Catalogue.objects.filter(customer_id=customer).filter(fidelity_program_id=fprogram).get().points
        if prev_points is not None:
            new_points = (prev_points + offset) if (prev_points + offset > 0) else 0.0
            Catalogue.objects.filter(customer_id=customer).filter(fidelity_program_id=fprogram).update(
                points=new_points)
        return

    def __str__(self):
        return '({program}, {csmr}, {pts})'.format(
            program=self.fidelity_program,
            csmr=self.customer,
            pts=self.points
        )


class Product(models.Model):
    name = models.CharField(max_length=30)
    value = models.FloatField(default=0.0)
    points_coefficient = models.FloatField(null=True)
    prize_coefficient = models.FloatField(null=True)
    is_persistent = models.BooleanField(default=False)

    # Database relationships
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='product_shop'
    )
    fidelity_program = models.ForeignKey(
        FidelityProgram,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='product_fidelity_program'
    )

    owning_users = models.ManyToManyField(User, blank=True, related_name='owners')

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = '5. Products'
        constraints = [
            models.UniqueConstraint(fields=['name', 'shop'], name='product_key')
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if self.fidelity_program is not None and not self.shop.fidelity_program_set.exists():
        if self.fidelity_program is not None and self.shop not in self.fidelity_program.shop_list.all():
            self.fidelity_program = None
        if self.fidelity_program is not None and self.points_coefficient is None:
            self.points_coefficient = self.fidelity_program.points_coefficient
        if self.fidelity_program is not None and self.prize_coefficient is None:
            self.prize_coefficient = self.fidelity_program.prize_coefficient

    def compute_points_variation(self):
        # if self.value == 0.0:
        #    return self.points_coefficient
        if self.points_coefficient is not None:
            return self.value * self.points_coefficient
        if self.fidelity_program is not None:
            return self.value * self.fidelity_program.points_coefficient
        return 0.0

    def compute_value_variation(self, total=None):
        if (self.value == 0.0) and (self.prize_coefficient is not None) and (total is not None):
            return total * self.prize_coefficient  # discount on total transaction
        if total is not None:
            return self.value  # normal earnable prize, if is persistent.
        if self.prize_coefficient is not None:
            return self.value * self.prize_coefficient  # cashback or discount
        if self.fidelity_program is not None:
            return self.value * self.fidelity_program.prize_coefficient
        # For every other situation, no variation occurs
        return self.value

    def add_user_owning_product(self, user: User):
        if self.is_persistent and Catalogue.objects.filter(customer=user).filter(
            fidelity_program=self.fidelity_program).filter(points__gte=self.value).exists():
            self.save()
            self.owning_users.add(user)
            self.save()

    def remove_user_owning_product(self, user: User):
        if self.is_persistent:
            self.owning_users.remove(user)


class Transaction(models.Model):
    executed_at = models.DateTimeField(auto_now_add=True)
    total = models.FloatField(editable=False, default=0.0)

    # Database relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transaction_user',
        null=True
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='transaction_shop',
        null=True
    )
    shopping_cart = models.ManyToManyField(Product)

    class Meta:
        verbose_name = 'transaction'
        verbose_name_plural = '6. Transactions'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if Transaction.objects.filter(id=self.id).count() == 0:
            super().save()

    def save(self, *args, **kwargs):
        if self.shopping_cart.exists():
            # if product is a non persistent prize available for this order only
            for product in self.shopping_cart.filter(is_persistent=False):
                self.update_total(product.compute_value_variation())
                if product.fidelity_program is not None:
                    Catalogue.update_points(self.user.username, product.fidelity_program.name,
                                            product.compute_points_variation())
            for product in self.shopping_cart.filter(is_persistent=True):
                if product.fidelity_program is not None and self.user not in product.owning_users.all():
                    product.add_user_owning_product(self.user)
                    self.update_total(product.compute_value_variation(self.total))
                    Catalogue.update_points(self.user.username, product.fidelity_program.name, product.compute_points_variation())
                # if product is a persistent prize owned by user
                if self.user in product.owning_users.all():
                    Catalogue.update_points(self.user, product.fidelity_program, product.compute_points_variation())
                    product.remove_user_owning_product(self.user)
        if self.total < 0:
            self.total = 0.0
        super(Transaction, self).save(*args, **kwargs)

    def update_total(self, offset: float):
        self.total += offset
