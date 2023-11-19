from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Shop


def resource_full_url(objpath):
    """
    Converts the given relative resource 
    path to an absolute one, by associating
    the domain path.
    """
    return f'http://testserver{objpath}'


# Create your tests here.

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.get_or_create(username="Marco91",
                                   password="marcorossi#91",
                                   bio="Hello World!",
                                   location="Camerino")

    def test_create_user(self):
        """ Should correctly store user """
        # self.user.save()
        stored_user = User.objects.get(username="Marco91")
        self.assertEqual(stored_user.username, "Marco91")
        # self.assertTrue(stored_user.groups.filter(name='Customer').exists())

    def test_delete_user(self):
        """ Should correctly delete user """
        User.objects.filter(username="Marco91").delete()
        self.assertEqual(User.objects.count(), 0)

    def test_user_update(self):
        """ Should correctly update user """
        User.objects.filter(username="Marco91").update(bio='New bio!')
        self.assertEqual(User.objects.get().bio, 'New bio!')

    def test_user_no_duplicate(self):
        """ Should not create a duplicated user """
        with self.assertRaises(IntegrityError):
            User.objects.create(username="Marco91",
                                password="marcorossipollo9",
                                bio="I am a copy!",
                                location="Camerino")


class UserAPITestCase(APITestCase):
    def test_api_create_user(self):
        """ 
        Should create and store a new user through 
        POST request 
        """
        # url = reverse('user')
        data = {'username': 'Marco91',
                'password': 'marcorossi#91',
                'email': 'marco.rossi@unicam.it',
                'bio': 'HelloWorld!',
                'location': 'Camerino'}
        response = self.client.post('/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'Marco91')

    def test_api_retrieve_user(self):
        """ 
        Should retrieve stored users through 
        GET request 
        """
        user = {
            'username': 'Marco91',
            'password': 'marcorossi#91',
            'email': 'samuele.stronati@unicam.it',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        another_user = {
            'username': 'Luca91',
            'password': 'lucarossi#91',
            'email': 'luca.rossi@unicam.it',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        self.client.post('/users/', user, format='json')
        self.client.post('/users/', another_user, format='json')
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(username='Marco91').exists())
        self.assertTrue(User.objects.filter(username='Luca91').exists())

    def test_api_update_user(self):
        """ 
        Should update stored users through 
        PUT request 
        """
        user = {
            'username': 'Marco91',
            'password': 'marcorossi#91',
            'email': 'samuele.stronati@unicam.it',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        new_bio_user = {
            'username': 'Marco91',
            'password': 'marcorossi#91',
            'email': 'samuele.stronati@unicam.it',
            'bio': 'New bio!',
            'location': 'Camerino'
        }
        self.client.post('/users/', user, format='json')
        response = self.client.put('/users/Marco91/', new_bio_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'Marco91')
        self.assertEqual(User.objects.get().bio, 'New bio!')

    def test_api_delete_users(self):
        """ 
        Should delete stored users through 
        DELETE request
        """
        user = {
            'username': 'Marco91',
            'password': 'marcorossi#91',
            'email': 'samuele.stronati@unicam.it',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        another_user = {
            'username': 'Luca91',
            'password': 'lucarossi#91',
            'email': 'luca.rossi@unicam.it',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        self.client.post('/users/', user, format='json')
        self.client.post('/users/', another_user, format='json')
        response = self.client.delete('/users/Marco91/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)
        self.assertFalse(User.objects.filter(username='Marco91').exists())
        self.assertTrue(User.objects.filter(username='Luca91').exists())


class ShopTestCase(TestCase):
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

