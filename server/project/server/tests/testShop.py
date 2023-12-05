from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from server.models import User, Shop


def resource_full_url(objpath):
    """
    Converts the given relative resource 
    path to an absolute one, by associating
    the domain path.
    """
    return f'http://testserver{objpath}'

class ShopTestCase(TestCase):
    """
    Test for Shop Model element CRUD operations
    """
    def setUp(self):
        self.shop_admin = User.objects.get_or_create(
            username="Marco91",
            password="marcorossi#91",
            bio="I own a shop!",
            location="Camerino"
        )
        self.employee = User.objects.get_or_create(
            username="Luca91",
            password="lucarossi#91",
            bio="I am an employee!",
            location="Camerino"
        )
        self.shop = Shop(
            name='La buona pizza',
            email='buona.pizza@gmail.com',
            phone='+393271234567',
            location='Camerino',
            owner_id="Marco91"
        )
        self.shop.employees.add("Luca91")
        self.shop.save()

    def test_create_shop(self):
        """ Should correctly store shop """
        stored_shop = Shop.objects.get(name='La buona pizza')
        self.assertEqual(stored_shop.email, 'buona.pizza@gmail.com')

    def test_delete_shop(self):
        """ Should correctly delete shop """
        Shop.objects.filter(name='La buona pizza').delete()
        self.assertEqual(Shop.objects.count(), 0)

    def test_update_shop(self):
        """ Should correctly update shop """
        Shop.objects.filter(name='La buona pizza').update(
            email='buona.pizza99@gmail.com')
        self.assertEqual(Shop.objects.get().email,
                         'buona.pizza99@gmail.com')

    def test_shop_no_duplicate_name_or_email(self):
        """ Should not create a duplicated shop """
        with self.assertRaises(IntegrityError):
            Shop.objects.create(
                name='La buona pizza',
                email='buona.pizza99@gmail.com',
                phone='+393271234567',
                location='Camerino',
                owner_id="Luca91"
            )
            Shop.objects.create(
                name='Pizza pazza',
                email='buona.pizza@gmail.com',
                phone='+393271234567',
                location='Camerino',
                owner_id="Luca91"
            )

class ShopAPITestCase(APITestCase):
    """
    Test REST API consumption for 
    Shop Model Element
    """
    def setUp(self):
        self.shop_admin = User.objects.get_or_create(
            username="Marco91",
            password="marcorossi#91",
            bio="I own a shop!",
            location="Camerino"
        )
        self.employee = User.objects.get_or_create(
            username="Luca91",
            password="lucarossi#91",
            bio="I am an employee!",
            location="Camerino"
        )

    def test_api_create_shop(self):
        """ 
        Should create and store a new shop through 
        POST request 
        """
        owner_url = reverse('user-detail', kwargs={'pk': 'Marco91'})
        data = {
            'name': 'La buona pizza',
            'email': 'buona.pizza@gmail.com',
            'phone': '+393271234567',
            'location': 'Camerino',
            'owner': resource_full_url(owner_url)
        }
        response = self.client.post('/shops/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shop.objects.count(), 1)
        self.assertEqual(Shop.objects.get().name, 'La buona pizza')

    def test_api_retrieve_shop(self):
        """ 
        Should retrieve stored shops through 
        GET request 
        """
        first_user_url = reverse('user-detail', kwargs={'pk': 'Marco91'})
        second_user_url = reverse('user-detail', kwargs={'pk': 'Luca91'})
        shop = {
            'name': 'La buona pizza',
            'email': 'buona.pizza@gmail.com',
            'phone': '+393271234567',
            'location': 'Camerino',
            'owner': resource_full_url(first_user_url),
            'employees': [resource_full_url(second_user_url)]
        }
        another_shop = {
            'name': 'Evergreen shop',
            'email': 'eshop@gmail.com',
            'phone': '+393271234567',
            'location': 'Roma',
            'owner': resource_full_url(second_user_url)
        }
        self.client.post('/shops/', shop, format='json')
        self.client.post('/shops/', another_shop, format='json')
        response = self.client.get('/shops/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Shop.objects.count(), 2)
        self.assertTrue(Shop.objects.filter(name='La buona pizza').exists())
        self.assertTrue(Shop.objects.filter(name='Evergreen shop').exists())

    def test_api_update_shop(self):
        """ 
        Should update stored shops through 
        PUT request 
        """
        first_user_url = reverse('user-detail', kwargs={'pk': 'Marco91'})
        second_user_url = reverse('user-detail', kwargs={'pk': 'Luca91'})
        shop = {
            'name': 'La buona pizza',
            'email': 'buona.pizza@gmail.com',
            'phone': '+393271234567',
            'location': 'Camerino',
            'owner': resource_full_url(first_user_url),
        }
        new_shop = {
            'name': 'La buona pizza',
            'email': 'buona.pizza@gmail.com',
            'phone': '+393271234567',
            'location': 'Camerino',
            'owner': resource_full_url(first_user_url),
            'employees': [resource_full_url(second_user_url)]
        }
        check_employee = User(
            username="Luca91",
            password="lucarossi#91",
            bio="I am an employee!",
            location="Camerino"
        )
        self.client.post('/shops/', shop, format='json')
        response = self.client.put('/shops/La buona pizza/', new_shop, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Shop.objects.count(), 1)
        self.assertEqual(Shop.objects.get().name, 'La buona pizza')
        self.assertEqual(check_employee.shop_set.count(), 1)

    def test_api_delete_shop(self):
        """ 
        Should delete stored shops through 
        DELETE request 
        """
        owner_url = reverse('user-detail', kwargs={'pk': 'Marco91'})
        shop = {
            'name': 'La buona pizza',
            'email': 'buona.pizza@gmail.com',
            'phone': '+393271234567',
            'location': 'Camerino',
            'owner': resource_full_url(owner_url),
        }
        another_shop = {
            'name': 'Evergreen shop',
            'email': 'eshop@gmail.com',
            'phone': '+393271234567',
            'location': 'Roma',
            'owner': resource_full_url(owner_url)
        }
        self.client.post('/shops/', shop, format='json')
        self.client.post('/shops/', another_shop, format='json')
        response = self.client.delete('/shops/La buona pizza/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Shop.objects.count(), 1)
        self.assertFalse(Shop.objects.filter(name='La buona pizza').exists())
        self.assertTrue(Shop.objects.filter(name='Evergreen shop').exists())
