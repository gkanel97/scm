import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password

class RegistrationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a test user group
        test_group = Group.objects.create(name='testers')
        test_group.save()
        # Create a test user in the test user group
        username = 'testuser'
        hashed_password = make_password('testpass123')
        test_user = User.objects.create(username=username, password=hashed_password)
        test_user.groups.add(test_group)
        test_user.save()
        
    def test_registration_valid(self):
        # Create a test user group
        url = reverse('create_group')
        data = {
            'group_name': 'testers-1'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.json())    

        # Create a test user in the test user group
        url = reverse('create_user')
        data = {
            'username': 'testuser-1',
            'password': 'testpass123',
            'group': 'testers-1'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.json())

    def test_registration_invalid_username(self):

        # Create a test user in the test user group
        url = reverse('create_user')
        data = {
            'username': 'testuser-2',
            'password': 'testpass123',
            'group': 'testers'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.json())    

        # Try to create a user with the same username
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        response_parsed = response.json()   
        self.assertEqual('username-exists', response_parsed['error'])

    def test_registration_invalid_group(self):

        # Try to create a user with an invalid group
        url = reverse('create_user')
        data = {
            'username': 'testuser-3',
            'password': 'testpass123',
            'group': 'tester-3'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        response_parsed = response.json()
        self.assertEqual('group-invalid', response_parsed['error'])

    def test_login_valid(self):

        url = reverse('login_user')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        # Try to login with valid credentials
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_login_invalid(self):

        url = reverse('login_user')
        data = {
            'username': 'testuser-2',
            'password': 'testpass1234'
        }
        # Try to login with invalid credentials
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 401)