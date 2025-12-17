from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from igaveapp.models import Receipt
from datetime import date


class APIAuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="apiuser",
            password="testpass123",
        )

    def test_obtain_token(self):
        response = self.client.post(
            "/api/token/",
            {"username": "apiuser", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {"username": "apiuser", "password": "wrong"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReceiptAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="receiptuser",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_receipt(self):
        data = {
            "store_name": "API Store",
            "date": date.today().isoformat(),
            "total_amount": "100.00",
        }
        response = self.client.post("/api/receipts/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Receipt.objects.count(), 1)
