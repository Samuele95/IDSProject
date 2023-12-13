from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from server.models import User, Shop, FidelityProgram, Catalogue, Product, Transaction
import json

class TransactionTestCase(TestCase):
    def setUp(self):
        self.shop_admin = User.objects.get_or_create(
            username="Marco91",
            password="marcorossi#91",
            bio="I own a shop!",
            location="Camerino"
        )
        self.customer = User.objects.get_or_create(
            username="Luca91",
            password="lucarossi#91",
            bio="I am an employee!",
            location="Camerino"
        )
        self.shop = Shop.objects.get_or_create(
            name='La buona pizza',
            email='buona.pizza@gmail.com',
            phone='+393271234567',
            location='Camerino',
            owner_id="Marco91"
        )

        self.fidelity_program = FidelityProgram(
            name='Programma fedeltà',
            program_type=FidelityProgram.POINTS,
            description='Test fidelity program',
            points_coefficient=0.8,
            prize_coefficient=0.8
        )
        self.fidelity_program.save()
        self.fidelity_program.shop_list.add('La buona pizza')
        self.fidelity_program.save()
        self.product, product_success = Product.objects.get_or_create(
            name='Pizza margherita',
            value=5.0,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
        )
        self.another_product, product_success = Product.objects.get_or_create(
            name='Pizza diavola',
            value=5.5,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
        )
        self.last_product, product_success = Product.objects.get_or_create(
            name='Pizza capricciosa',
            value=6.0,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
        )

        self.stored_user, catalogue_success = Catalogue.objects.get_or_create(
            customer_id='Luca91',
            fidelity_program_id='Programma fedeltà',
            points=0.0
        )

        self.transaction= Transaction(
            user_id='Luca91',
            shop_id='La buona pizza',
        )

        self.transaction.shopping_cart.add(
            Product.objects.get(name='Pizza diavola'),
            Product.objects.get(name='Pizza margherita')
        )
        self.transaction.save()

    def test_create_transaction(self):
        """ Should correctly store transaction """
        self.assertEqual(Transaction.objects.all().count(), 1)
        self.assertEqual(Catalogue.objects.get().points, 8.4)

    def test_retrieve_transaction(self):
        """ Should correctly retrieve transaction """
        self.assertEqual(Transaction.objects.get().total, 8.4)
        self.assertEqual(Transaction.objects.get().shopping_cart.all().count(), 2)

    def test_update_transaction(self):
        """ Should correctly update transaction """
        Transaction.objects.filter(id=1).update(
            total=10.0
        )
        self.assertEqual(Transaction.objects.get().total, 10.0)

    def test_delete_transaction(self):
        """ Should correctly delete transaction """
        Transaction.objects.filter(id=1).delete()
        self.assertEqual(Transaction.objects.all().count(), 0)

    #def test_no_cascade_shop_delete(self):
    #    """
    #    Should correctly delete transaction
    #    when associated shop is deleted
    #    """
    #    Shop.objects.filter(name='La buona pizza').delete()
    #    self.assertEqual(Transaction.objects.all().count(), 1)

    #def test_no_cascade_user_delete(self):
    #    """
    #    Should correctly delete transaction
    #    when associated user is deleted
    #    """
    #    User.objects.filter(username='Luca91').delete()
    #    self.assertEqual(Transaction.objects.all().count(), 1)