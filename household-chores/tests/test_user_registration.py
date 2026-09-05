import unittest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class UserRegistrationAPITest(APITestCase):
    """Test cases for user registration API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.register_url = reverse('register_user')
        self.login_url = reverse('user_login')
        self.profile_url = reverse('get_user_profile')
    
    def test_successful_user_registration(self):
        """Test successful user registration."""
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
        self.assertEqual(User.objects.get().name, 'Test User')
    
    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch."""
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpass123',
            'password_confirm': 'differentpass123'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_registration_missing_required_fields(self):
        """Test user registration with missing required fields."""
        data = {
            'email': 'test@example.com',
            'name': '',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_user_registration_duplicate_email(self):
        """Test user registration with duplicate email."""
        User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        
        data = {
            'email': 'test@example.com',
            'name': 'Another User',
            'password': 'testpass456',
            'password_confirm': 'testpass456'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_successful_user_login(self):
        """Test successful user login."""
        user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_get_user_profile_unauthenticated(self):
        """Test getting user profile without authentication."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_user_profile_authenticated(self):
        """Test getting user profile with authentication."""
        user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def test_user_creation(self):
        """Test user creation."""
        user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_str_method(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        
        expected_str = 'Test User (test@example.com)'
        self.assertEqual(str(user), expected_str)