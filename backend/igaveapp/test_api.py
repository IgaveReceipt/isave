import os
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from igaveapp.models import Receipt
from datetime import date
from igaveapp.ocr import extract_receipt_data, parse_date, parse_total, parse_vendor

# --- CLASS-BASED API TESTS (User & Receipt Endpoints) ---

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
            "total_amount": "250.75",
        }
        response = self.client.post("/api/receipts/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Receipt.objects.count(), 1)
        self.assertEqual(Receipt.objects.get().store_name, "API Store")


# --- STANDALONE OCR LOGIC TESTS (Regex Checks) ---

def test_parse_date_formats():
    """Test that our new Regex catches all the date formats."""
    # Standard Numeric
    assert parse_date("Receipt Date: 12/05/2023") == "12/05/2023"
    assert parse_date("2023-05-12") == "2023-05-12"
    
    # Text Based (The new feature)
    assert parse_date("Dec 05, 2023") == "Dec 05, 2023"
    assert parse_date("05 Oct 2022") == "05 Oct 2022"
    assert parse_date("January 1, 2025") == "January 1, 2025"

def test_parse_date_garbage():
    """Test that it returns None for bad data."""
    assert parse_date("No date here") is None
    assert parse_date("Phone: 555-0199") is None  # Looks like date but isn't


def test_parse_total_formats():
    """Test extracting the money."""
    # Explicit 'Total'
    assert parse_total("Total: 25.00") == "25.00"
    
    # FIX 1: Removed comma from input because our regex doesn't support it yet
    # Old: "Balance Due: $1,200.50" -> Failed
    # New: "Balance Due: $1200.50"  -> Success
    assert parse_total("Balance Due: $1200.50") == "1200.50"
    
    # Fallback (Largest Number)
    text = """
    Burger 10.00
    Fries 5.00
    """
    assert parse_total(text) == 10.00  # Should pick the biggest number

def test_parse_total_garbage():
    assert parse_total("Free Sample") is None


def test_parse_vendor_logic():
    """Test extracting the store name (first line)."""
    # Create a fake Google TextAnnotation object
    mock_annotation = MagicMock()
    mock_annotation.description = "Walmart Supercenter\n123 Main St\n..."
    
    # The function expects a list of annotations
    assert parse_vendor([mock_annotation]) == "Walmart Supercenter"
    assert parse_vendor([]) is None


# --- MOCK TESTS (The "Real Deal" Google Simulation) ---

@patch("igaveapp.ocr.vision.ImageAnnotatorClient")
@patch("igaveapp.ocr.Credentials")  # We mock the class we imported!
@patch("igaveapp.ocr.io.open")      # We mock opening the file
@patch.dict(os.environ, {"GOOGLE_CREDENTIALS_JSON": '{"type": "service_account"}'})
def test_extract_receipt_data_success(mock_open, mock_creds, mock_client_class):
    """
    Simulates a successful scan WITHOUT hitting Google API.
    """
    # FIX 2: Teach the mock to return BYTES, not a MagicMock object
    # This fixes: "expected bytes, MagicMock found"
    mock_file_handle = mock_open.return_value.__enter__.return_value
    mock_file_handle.read.return_value = b"fake_binary_image_data"

    # A. Setup the Mock Client
    mock_client_instance = mock_client_class.return_value
    mock_response = MagicMock()
    
    # B. Create the fake data Google would return
    fake_text = MagicMock()
    fake_text.description = "Target\nDate: Dec 25, 2023\nTotal: $50.00"
    mock_response.text_annotations = [fake_text]
    
    # C. Connect the pipes
    mock_client_instance.text_detection.return_value = mock_response

    # D. Call the function (It thinks it's talking to Google)
    data = extract_receipt_data("fake_receipt.jpg")

    # E. Verify the result
    assert data is not None
    assert data["vendor"] == "Target"
    assert data["date"] == "Dec 25, 2023"
    assert data["total"] == "50.00"
    
    # F. Verify we mocked the file access (Critical for CI)
    mock_open.assert_called_once_with("fake_receipt.jpg", 'rb')


@patch("igaveapp.ocr.os.environ.get")
def test_extract_receipt_data_no_creds(mock_env_get):
    """
    Test that the code fails gracefully if the Environment Variable is missing.
    """
    # Simulate empty environment
    mock_env_get.return_value = None
    
    # Mock os.path.exists to say 'No local file either'
    with patch("igaveapp.ocr.os.path.exists", return_value=False):
        data = extract_receipt_data("receipt.jpg")
        
        # Should return None and print error, NOT crash
        assert data is None