from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from server.models import User, Shop, FidelityProgram


def resource_full_url(objpath):
    """
    Converts the given relative resource 
    path to an absolute one, by associating
    the domain path.
    """
    return f'http://testserver{objpath}'

class FidelityProgramTestCase(TestCase):
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

        self.fidelity_program = FidelityProgram(
            name='Programma fedeltà',
            program_type=FidelityProgram.POINTS,
            description='Test fidelity program',
            points_coefficient=0.5,
            prize_coefficient=0.5
        )
        self.fidelity_program.save()
        self.fidelity_program.shop_list.add('La buona pizza')
        self.fidelity_program.save()

    def test_create_fidelity_program(self):
        """ Should correctly store fidelity program """
        stored_fp = FidelityProgram.objects.get()
        self.assertEqual(stored_fp.description, 'Test fidelity program')

    def test_update_fidelity_program(self):
        """ Should update stored fidelity program """
        FidelityProgram.objects.filter(name='Programma fedeltà').update(
            description='New Fidelity program!')
        self.assertEqual(FidelityProgram.objects.get().description,
                         'New Fidelity program!')

    def test_delete_fidelity_program(self):
        """ Should delete stored fidelity program """
        FidelityProgram.objects.filter(name='Programma fedeltà').delete()
        self.assertEqual(FidelityProgram.objects.count(), 0)

    def test_is_coalition(self):
        """ 
        Should return true when more than one
        shop instance is bound to the given
        fidelity program, false otherwise
        """
        self.assertFalse(self.fidelity_program.is_coalition())
        another_shop = Shop(
            name='Evergreen market',
            email='evergreen@gmail.com',
            phone='+393271234567',
            location='Matelica',
            owner_id="Luca91"
        )
        another_shop.save()
        self.fidelity_program.shop_list.add('Evergreen market')
        self.assertTrue(self.fidelity_program.is_coalition())


class FidelityProgramAPITestCase(APITestCase):
    def setUp(self):
        self.shop_admin = User.objects.get_or_create(
            username="Marco91",
            password="marcorossi#91",
            bio="I own a shop!",
            location="Camerino"
        )
        self.another_admin = User.objects.get_or_create(
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
        self.another_shop = Shop.objects.get_or_create(
            name='Evergreen market',
            email='evergreen@gmail.com',
            phone='+393271234567',
            location='Matelica',
            owner_id="Luca91"
        )

    def test_api_create_fidelity_program(self):
        """ 
        Should create and store a new fidelity program through 
        POST request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        data = {
            'name': 'Programma fedeltà',
            'program_type': FidelityProgram.POINTS,
            'description': 'Test fidelity program',
            'shop_list': [resource_full_url(shop_url)]
        }
        response = self.client.post('/fidelityprograms/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FidelityProgram.objects.count(), 1)
        self.assertEqual(FidelityProgram.objects.get().name, 'Programma fedeltà')
    
    def test_api_create_cashback_program(self):
        """ 
        Should create and store a new CASHBACK program through 
        POST request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        data = {
            'name': 'Programma fedeltà',
            'program_type': FidelityProgram.CASHBACK,
            'description': 'Test fidelity program',
            'shop_list': [resource_full_url(shop_url)]
        }
        response = self.client.post('/fidelityprograms/cashbackprograms/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FidelityProgram.objects.count(), 1)
        self.assertEqual(FidelityProgram.objects.get().name, 'Programma fedeltà')  
        self.assertEqual(FidelityProgram.objects.get().points_coefficient, -0.5)
        self.assertEqual(FidelityProgram.objects.get().prize_coefficient, -0.5) 
    
    def test_api_create_points_program(self):
        """ 
        Should create and store a new POINTS program through 
        POST request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        data = {
            'name': 'Programma fedeltà',
            'program_type': FidelityProgram.POINTS,
            'description': 'Test fidelity program',
            'shop_list': [resource_full_url(shop_url)]
        }
        response = self.client.post('/fidelityprograms/pointsprograms/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FidelityProgram.objects.count(), 1)
        self.assertEqual(FidelityProgram.objects.get().name, 'Programma fedeltà')  
        self.assertEqual(FidelityProgram.objects.get().points_coefficient, 0.5)
        self.assertEqual(FidelityProgram.objects.get().prize_coefficient, 0.5) 

    def test_api_retrieve_fidelity_program(self):
        """ 
        Should retrieve stored fidelity programs through 
        GET request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        another_shop_url = reverse('shop-detail', kwargs={'pk': 'Evergreen market'})
        fidelity_program = {
            'name': 'Programma fedelta',
            'program_type': FidelityProgram.POINTS,
            'description': 'Test fidelity program',
            'shop_list': [resource_full_url(shop_url)]
        }
        another_fidelity_program = {
            'name': 'Another program',
            'program_type': FidelityProgram.LEVELS,
            'description': 'I am just a copy!!',
            'shop_list': [resource_full_url(another_shop_url)]
        }
        self.client.post(
            '/fidelityprograms/',
            fidelity_program,
            format='json'
        )
        self.client.post(
            '/fidelityprograms/',
            another_fidelity_program,
            format='json'
        )
        response = self.client.get('/fidelityprograms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FidelityProgram.objects.count(), 2)
        self.assertTrue(FidelityProgram.objects.
                        filter(name='Programma fedelta').exists())
        self.assertTrue(FidelityProgram.objects.
                        filter(name='Another program').exists())

    def test_api_update_fidelity_program(self):
        """ 
        Should update stored fidelity programs through 
        PUT request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        another_shop_url = reverse('shop-detail', kwargs={'pk': 'Evergreen market'})
        fidelity_program = {
            'name': 'Programma fedelta',
            'program_type': FidelityProgram.POINTS,
            'description': 'Test fidelity program',
            'shop_list': [resource_full_url(shop_url)]
        }
        updated_fidelity_program = {
            'name': 'Programma fedelta',
            'program_type': FidelityProgram.POINTS,
            'description': 'Test fidelity program',
            'shop_list': [
                resource_full_url(shop_url),
                resource_full_url(another_shop_url)
            ]
        }
        self.assertEqual(
            self.client.post(
                '/fidelityprograms/',
                fidelity_program,
                format='json'
            ).status_code,
            status.HTTP_201_CREATED
        )
        response = self.client.put(
            '/fidelityprograms/Programma fedelta/',
            updated_fidelity_program,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FidelityProgram.objects.count(), 1)
        self.assertTrue(FidelityProgram.objects.get().is_coalition())

    def test_api_delete_fidelity_program(self):
        """ 
        Should delete stored fidelity programs through 
        DELETE request 
        """
        shop_url = reverse('shop-detail', kwargs={'pk': 'La buona pizza'})
        another_shop_url = reverse('shop-detail', kwargs={'pk': 'Evergreen market'})
        fidelity_program = {
            'name': 'Programma fedelta',
            'program_type': FidelityProgram.POINTS,
            'description': 'Test fidelity program',
            'shop_list': [resource_full_url(shop_url)]
        }
        another_fidelity_program = {
            'name': 'Another program',
            'program_type': FidelityProgram.LEVELS,
            'description': 'I am just a copy!!',
            'shop_list': [resource_full_url(another_shop_url)]
        }
        self.client.post(
            '/fidelityprograms/',
            fidelity_program,
            format='json'
        )
        self.client.post(
            '/fidelityprograms/',
            another_fidelity_program,
            format='json'
        )
        response = self.client.delete('/fidelityprograms/Programma fedelta/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FidelityProgram.objects.count(), 1)
        self.assertFalse(FidelityProgram.objects.filter(name='Programma fedelta').exists())
        self.assertTrue(FidelityProgram.objects.filter(name='Another program').exists())
