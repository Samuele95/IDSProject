from django.test import TestCase
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from server.models import User


def resource_full_url(objpath):
    """
    Converts the given relative resource 
    path to an absolute one, by associating
    the domain path.
    """
    return f'http://testserver{objpath}'


# Create your tests here.

class UserTestCase(TestCase):
    """
    Test for User Model element CRUD operations
    """
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
    """
    Test REST API consumption for 
    User Model Element
    """
    def test_api_create_user(self):
        """ 
        Should create and store a new user through 
        POST request 
        """
        data = {'username': 'Marco91',
                'password': 'marcorossi#91',
                'email': 'marco.rossi@unicam.it',
                'phone': '+393271234567',
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
            'phone': '+393271234567',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        another_user = {
            'username': 'Luca91',
            'password': 'lucarossi#91',
            'email': 'luca.rossi@unicam.it',
            'phone': '+393271234567',
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
            'phone': '+393271234567',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        new_bio_user = {
            'username': 'Marco91',
            'password': 'marcorossi#91',
            'email': 'samuele.stronati@unicam.it',
            'phone': '+393271234567',
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
            'phone': '+393271234567',
            'bio': 'HelloWorld!',
            'location': 'Camerino'
        }
        another_user = {
            'username': 'Luca91',
            'password': 'lucarossi#91',
            'email': 'luca.rossi@unicam.it',
            'phone': '+393271234567',
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
