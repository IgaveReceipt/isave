# backend/igaveapp/ocr.py
import os
import io
import re
import json
from google.oauth2.service_account import Credentials
from google.cloud import vision

# BASE_DIR calculation broken into two lines to satisfy PEP8
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


def extract_receipt_data(file_path):
    """
    Scans a receipt using Google Cloud Vision API and 'guesses' the data.
    """
    client = None

    try:
        # 2. START THE CLIENT 🤖
        google_json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")

        if google_json_str:
            # Option A: Found the secure variable (Production/Local Secure)
            creds_dict = json.loads(google_json_str)
            # Import change makes this line much shorter now (Fixes E501)
            credentials = Credentials.from_service_account_info(creds_dict)
            client = vision.ImageAnnotatorClient(credentials=credentials)
        else:
            # 2. FALLBACK: Check for local file (Development only)
            creds_path = os.path.join(BASE_DIR, "google_credentials.json")

            if os.path.exists(creds_path):
                print(f"📂 Loading Google Credentials from file: {creds_path}")
                # Break long line
                client = vision.ImageAnnotatorClient.from_service_account_json(
                    creds_path
                )
            else:
                print("❌ CRITICAL ERROR: No Google Credentials found.")
                return None

        # 3. LOAD THE IMAGE 📸
        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # 4. SEND TO GOOGLE (TEXT_DETECTION) ☁️
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            print("❌ No text found in image.")
            return None

        # The first element [0] is the entire text blob
        full_text = texts[0].description

        # 5. PARSE THE DATA 🕵️‍♂️
        data = {
            "vendor": parse_vendor(texts),
            "date": parse_date(full_text),
            "total": parse_total(full_text),
            "category": "Uncategorized"
        }

        return data

    except Exception as e:
        print(f"❌ Google Vision Error: {e}")
        return None


# --- HELPER FUNCTIONS ---

def parse_vendor(texts):
    """
    Simple logic: Vendor is usually the text at the very top.
    """
    try:
        lines = texts[0].description.split('\n')
        if lines:
            # Strip whitespace from the first line
            return lines[0].strip()
        return "Unknown Vendor"
    except Exception:
        return None


def parse_date(text):
    """
    Regex to find dates.
    Now supports:
    1. Numeric: 12/05/2025, 2025-05-12
    2. Text:    Dec 05, 2025, 12 October 2023
    """
    # 1. Numeric Pattern (MM/DD/YYYY or YYYY-MM-DD)
    numeric_pattern = (
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|'
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
    )
    match = re.search(numeric_pattern, text)
    if match:
        return match.group(0)

    # 2. Text Pattern (Month Names)
    text_pattern = (
        r'(?i)\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*'
        r'[\s,.-]+\d{1,2}[\s,.-]+\d{2,4}|'
        r'\d{1,2}[\s,.-]+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
        r'[a-z]*[\s,.-]+\d{2,4})\b'
    )

    match = re.search(text_pattern, text)
    if match:
        return match.group(0)

    return None


def parse_total(text):
    """
    Finds 'Total' or largest number.
    """
    # 1. Try to find "Total: $25.00"
    # Split regex string to fit PEP8 line length
    total_pattern = (
        r'(?i)(total|balance|amount|due)[\s:$]*(\d{1,5}\.\d{2})'
    )
    match = re.search(total_pattern, text)
    if match:
        return match.group(2)

    # 2. Fallback: Find ALL money-looking numbers and take the biggest
    money_pattern = r'\b\d{1,5}\.\d{2}\b'
    amounts = re.findall(money_pattern, text)

    if amounts:
        valid_amounts = [float(a) for a in amounts]
        return max(valid_amounts)

    return None
