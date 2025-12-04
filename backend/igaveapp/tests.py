from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from igaveapp.models import Receipt
from datetime import date


class BasicTest(TestCase):
    def test_basic_addition(self):
        self.assertEqual(1 + 1, 2)


class UserTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='password')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password'))


class ReceiptTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='receiptuser', password='password')

    def test_receipt_creation(self):
        receipt = Receipt.objects.create(
            user=self.user,
            store_name="Test Store",
            date=date.today(),
            total_amount=100.50
        )
        self.assertEqual(receipt.store_name, "Test Store")
        self.assertEqual(receipt.total_amount, 100.50)
        self.assertEqual(receipt.user, self.user)


class APIAuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            password='testpass123',
            email='api@test.com'
        )

    def test_obtain_token(self):
        """Test JWT token generation."""
        response = self.client.post('/api/token/', {
            'username': 'apiuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        response = self.client.post('/api/token/', {
            'username': 'apiuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReceiptAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='receiptapiuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_receipt(self):
        """Test creating a receipt via API."""
        data = {
            'store_name': 'API Store',
            'date': date.today().isoformat(),
            'total_amount': '250.75'
        }
        response = self.client.post('/api/receipts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Receipt.objects.count(), 1)
        self.assertEqual(Receipt.objects.get().store_name, 'API Store')

    def test_list_receipts(self):
        """Test listing receipts for authenticated user."""
        Receipt.objects.create(
            user=self.user,
            store_name='Store 1',
            date=date.today(),
            total_amount=100.00
        )
        Receipt.objects.create(
            user=self.user,
            store_name='Store 2',
            date=date.today(),
            total_amount=200.00
        )
        response = self.client.get('/api/receipts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_receipt_isolation(self):
        """Test that users can only see their own receipts."""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        Receipt.objects.create(
            user=other_user,
            store_name='Other Store',
            date=date.today(),
            total_amount=300.00
        )
        response = self.client.get('/api/receipts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access receipts."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/receipts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
