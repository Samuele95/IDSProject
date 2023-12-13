from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from server.models import User, Shop, FidelityProgram, Catalogue, Product, Transaction
import json

def resource_full_url(objpath):
    """
    Converts the given relative resource 
    path to an absolute one, by associating
    the domain path.
    """
    return f'http://testserver{objpath}'

class CatalogueTestCase(APITestCase):
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

        self.another_customer  = User.objects.get_or_create(
            username="Paolo91",
            password="paolorossi#91",
            bio="I am an employee!",
            location="Camerino"
        )

        self.last_customer  = User.objects.get_or_create(
            username="Claudio91",
            password="claudiorossi#91",
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

        self.another_shop = Shop.objects.get_or_create(
            name='Pizza pazza',
            email='pizza.pazza@gmail.com',
            phone='+393271234567',
            location='Camerino',
            owner_id="Marco91"
        )

        self.fidelity_program = FidelityProgram(
            name='Programma fedeltà',
            program_type=FidelityProgram.GENERIC,
            description='Test fidelity program',
        )

        self.another_fidelity_program = FidelityProgram(
            name='Programma punti',
            program_type=FidelityProgram.POINTS,
            description='Test fidelity program',
            points_coefficient=0.8,
            prize_coefficient=0.8
        )
        self.fidelity_program.save()
        self.fidelity_program.shop_list.add('La buona pizza')
        self.fidelity_program.save()

        self.another_fidelity_program.save()
        self.another_fidelity_program.shop_list.add('Pizza pazza')
        self.another_fidelity_program.save()

        self.product_one, product_success = Product.objects.get_or_create(
            name='Pizza margherita',
            value=5.0,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
        )

        self.product_two, product_success = Product.objects.get_or_create(
            name='Pizza margherita',
            value=4.0,
            shop_id='Pizza pazza',
            fidelity_program_id='Programma punti',
        )
        self.product_three, product_success = Product.objects.get_or_create(
            name='Pizza diavola',
            value=5.5,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
        )
        self.product_four, product_success = Product.objects.get_or_create(
            name='Pizza capricciosa',
            value=6.0,
            shop_id='Pizza pazza',
        )
        self.product_five, product_success = Product.objects.get_or_create(
            name='Pizza diavola',
            value=6.5,
            shop_id='Pizza pazza',
            fidelity_program_id='Programma punti',
        )

        self.prize_one, prize_success = Product.objects.get_or_create(
            name='Coupon di benvenuto',
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
            is_persistent=True
        )

        self.prize_two, prize_success = Product.objects.get_or_create(
            name='Sconto del 20%',
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
            is_persistent=True,
            points_coefficient=0.2,
            prize_coefficient=0.2
        )

        self.prize_three, prize_success = Product.objects.get_or_create(
            name='Coupon di benvenuto',
            shop_id='Pizza pazza',
            fidelity_program_id='Programma punti',
            is_persistent=True
        )

        self.prize_four, prize_success = Product.objects.get_or_create(
            name='Punti omaggio',
            shop_id='Pizza pazza',
            fidelity_program_id='Programma punti',
            value=3.0,
            points_coefficient=1.0,
            is_persistent=True
        )

        self.cat_user_one, catalogue_success = Catalogue.objects.get_or_create(
            customer_id='Luca91',
            fidelity_program_id='Programma fedeltà',
            points=0.0
        )

        self.cat_user_two, catalogue_success = Catalogue.objects.get_or_create(
            customer_id='Paolo91',
            fidelity_program_id='Programma punti',
            points=0.0
        )

        self.cat_user_three, catalogue_success = Catalogue.objects.get_or_create(
            customer_id='Claudio91',
            fidelity_program_id='Programma punti',
            points=10.0
        )

        self.cat_user_four, catalogue_success = Catalogue.objects.get_or_create(
            customer_id='Claudio91',
            fidelity_program_id='Programma fedeltà',
        )

    def test_api_retrieve_all_catalogue_elements(self):
        response = self.client.get('/catalogue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 4)

    def test_api_catalogue_elements_by_user(self):
        response_one = self.client.get('/catalogue/byuser/Claudio91/')
        response_two = self.client.get('/catalogue/byuser/Luca91/')
        self.assertEqual(response_one.status_code, status.HTTP_200_OK)
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_one.json()), 2)
        self.assertEqual(len(response_two.json()), 1)

    def test_api_catalogue_elements_by_program(self):
        response_one = self.client.get('/catalogue/byprogram/Programma punti/')
        response_two = self.client.get('/catalogue/byprogram/Programma fedeltà/')
        self.assertEqual(response_one.status_code, status.HTTP_200_OK)
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_one.json()), 2)
        self.assertEqual(len(response_two.json()), 2)

    def test_api_catalogue_elements_by_user_and_program(self):
        response_one = self.client.get('/catalogue/Claudio91/Programma punti/')
        response_two = self.client.get('/catalogue/Paolo91/Programma fedeltà/')
        user_url = reverse('user-detail', kwargs={'pk': 'Claudio91'})
        self.assertEqual(response_one.status_code, status.HTTP_200_OK)
        self.assertEqual(response_two.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_one.json()['customer'], resource_full_url(user_url))
    
    def test_api_available_prizes_for_user(self):
        response_one = self.client.get('/catalogue/available_prizes/Paolo91/Programma punti/')
        response_two = self.client.get('/catalogue/available_prizes/Claudio91/Programma punti/')
        #response_two = self.client.get('/catalogue/Paolo91/Programma fedeltà/')
        #user_url = reverse('user-detail', kwargs={'pk': 'Claudio91'})
        self.assertEqual(response_one.status_code, status.HTTP_200_OK)
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_one.json()), 1)
        self.assertEqual(len(response_two.json()), 2)
        