from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from server.models import User, Shop, FidelityProgram, Product
import json

def resource_full_url(objpath):
    """
    Converts the given relative resource 
    path to an absolute one, by associating
    the domain path.
    """
    return f'http://testserver{objpath}'

class ProductTestCase(TestCase):
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
        )
        self.fidelity_program.save()
        self.fidelity_program.shop_list.add('La buona pizza')
        self.fidelity_program.save()
        self.product, product_success = Product.objects.get_or_create(
            name='Pizza margherita',
            value=5.0,
            shop_id='La buona pizza',
        )

    def test_create_product(self):
        """ Should correctly store product """
        self.assertEquals(Product.objects.all().count(), 1)

    def test_retrieve_product(self):
        """ Should correctly retrieve product """
        self.assertEquals(Product.objects.get().name, 'Pizza margherita')


    def test_update_product(self):
        """ Should correctly update product """
        Product.objects.filter(id=1).update(
            value=5.5
        )
        self.assertEquals(Product.objects.get().value, 5.5)

    def test_delete_product(self):
        """ Should correctly delete product """
        Product.objects.create(
            name='Pizza diavola',
            shop_id='La buona pizza',
            value=6.0
        )
        self.assertEqual(Product.objects.all().count(), 2)
        Product.objects.filter(id=1).delete()
        self.assertEqual(Product.objects.all().count(), 1)
        self.assertFalse(Product.objects.filter(name='Pizza margherita').exists())
        self.assertTrue(Product.objects.filter(name='Pizza diavola').exists())

    def test_product_composite_key(self):
        """ 
        Should not create more product rows
        sharing same composite key (Name, Shop)
        """
        with self.assertRaises(IntegrityError):
            already_stored_element = Product.objects.create(
                name='Pizza margherita',
                shop_id='La buona pizza',
                value=6.0
            )

    def test_cascade_product_delete(self):
        """
        Should delete products when the associated
        shop is deleted from the database
        """
        Product.objects.create(
            name='Pizza diavola',
            shop_id='La buona pizza',
            value=6.0
        )
        self.assertEqual(Product.objects.all().count(), 2)
        Shop.objects.filter(name='La buona pizza').delete()
        self.assertEqual(Product.objects.all().count(), 0)

    def test_cascade_product_not_delete(self):
        """
        Should not delete products when the associated
        fidelity program is deleted from the database
        """
        another_product, product_success = Product.objects.get_or_create(
            name='Pizza diavola',
            value=5.0,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà'
        )
        self.assertEqual(Product.objects.all().count(), 2)
        FidelityProgram.objects.filter(name='Programma fedeltà').delete()
        self.assertEqual(Product.objects.all().count(), 2)

    def test_program_shop_coeherence(self):
        """
        Should associate a fidelity program to a product
        instance iff the product is owned by a shop which
        is associated to that fidelity program
        """
        Product.objects.filter(id=1).update(
            fidelity_program_id='Programma fedeltà'
        )
        Product.objects.create(
            name='Pizza diavola',
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
            value=6.0
        )
        Shop.objects.create(
            name='Auto assicurazioni',
            email='aassicurazioni@gmail.com',
            phone='+393271234567',
            location='Camerino'
        )
        Product.objects.create(
            name='Coupon omaggio',
            shop_id='Auto assicurazioni',
            fidelity_program_id='Programma fedeltà',
            value=0.0
        )
        self.assertIsNotNone(Product.objects.get(name='Pizza diavola').fidelity_program_id)
        self.assertIsNotNone(Product.objects.get(name='Pizza margherita').fidelity_program_id)
        self.assertIsNone(Product.objects.get(name='Coupon omaggio').fidelity_program_id)
        Product.objects.filter(id=1).update(
            shop_id='Auto assicurazioni'
        )
        self.assertIsNone(Product.objects.get(name='Pizza margherita').fidelity_program_id)

    def test_product_coefficients(self):
        self.assertIsNone(self.product.points_coefficient)
        self.assertIsNone(self.product.prize_coefficient)
        another_product, product_success = Product.objects.get_or_create(
            name='Pizza diavola',
            value=5.0,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà'
        )
        self.assertEqual(another_product.points_coefficient, 0.5)
        self.assertEqual(another_product.prize_coefficient, 0.5)
        complete_product, product_success = Product.objects.get_or_create(
            name='Pizza capricciosa',
            value=5.0,
            shop_id='La buona pizza',
            fidelity_program_id='Programma fedeltà',
            points_coefficient=0.8,
            prize_coefficient=0.7
        )
        self.assertEqual(complete_product.points_coefficient, 0.8)
        self.assertEqual(complete_product.prize_coefficient, 0.7)


class ProductAPITestCase(APITestCase):
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

        self.fidelity_program, result = FidelityProgram.objects.get_or_create(
            name='Programma fedelta',
            program_type=FidelityProgram.POINTS,
            description='Test fidelity program',
        )
        self.fidelity_program.shop_list.add('La buona pizza')
        self.fidelity_program.save()

    def test_api_create_product(self):
        """ 
        Should create and store a new product element through 
        POST request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        program_url = reverse('fidelityprogram-detail', kwargs={'pk': 'Programma fedelta'})
        data = {
            'name': 'Pizza margherita',
            'value': 5.0,
            'shop': resource_full_url(shop_url),
            'fidelity_program': resource_full_url(program_url)
        }
        response = self.client.post('/product/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, 'Pizza margherita')

    def test_api_retrieve_product(self):
        """ 
        Should retrieve product element through 
        GET request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        program_url = reverse('fidelityprogram-detail', kwargs={'pk': 'Programma fedelta'})
        data = {
            'name': 'Pizza margherita',
            'value': 5.0,
            'shop': resource_full_url(shop_url),
            'fidelity_program': resource_full_url(program_url)
        }
        another_data = {
            'name': 'Pizza diavola',
            'value': 5.5,
            'shop': resource_full_url(shop_url),
        }
        self.client.post('/product/', data, format='json')
        self.client.post('/product/', another_data, format='json')
        self.assertEqual(Product.objects.count(), 2)
        response = self.client.get('/product/')
        expected_response = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": "http://testserver/product/1/",
                    "id": 1,
                    "name": "Pizza margherita",
                    "value": 5.0,
                    "points_coefficient": 0.5,
                    "prize_coefficient": 0.5,
                    "is_persistent": False,
                    "shop": "http://testserver/shops/La%20buona%20pizza/",
                    "fidelity_program": "http://testserver/fidelityprograms/Programma%20fedelta/",
                    "owning_users": []
                },
                {
                    "url": "http://testserver/product/2/",
                    "id": 2,
                    "name": "Pizza diavola",
                    "value": 5.5,
                    "points_coefficient": None,
                    "prize_coefficient": None,
                    "is_persistent": False,
                    "shop": "http://testserver/shops/La%20buona%20pizza/",
                    "fidelity_program": None,
                    "owning_users": []
                }
            ]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), expected_response)

    def test_api_delete_product(self):
        """ 
        Should delete a product element through 
        DELETE request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        program_url = reverse('fidelityprogram-detail', kwargs={'pk': 'Programma fedelta'})
        data = {
            'name': 'Pizza margherita',
            'value': 5.0,
            'shop': resource_full_url(shop_url),
            'fidelity_program': resource_full_url(program_url)
        }
        another_data = {
            'name': 'Pizza diavola',
            'value': 5.5,
            'shop': resource_full_url(shop_url),
        }
        self.client.post('/product/', data, format='json')
        self.client.post('/product/', another_data, format='json')
        self.assertEqual(Product.objects.count(), 2)
        response = self.client.delete('/product/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)
        self.assertFalse(Product.objects.filter(pk=1).exists())
        self.assertTrue(Product.objects.filter(pk=2).exists())