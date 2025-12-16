# backend/igaveapp/ocr.py
import os
import io
import re 
from google.cloud import vision
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "google_credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

def extract_receipt_data(file_path):
    """
    Scans a receipt using Google Cloud Vision API and 'guesses' the data.
    """

    if not os.path.exists(CREDENTIALS_PATH):
        print(f"❌ Error: Google Key not found at {CREDENTIALS_PATH}")
        return None

    try:
        # 2. START THE CLIENT 🤖
        client = vision.ImageAnnotatorClient()

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
        print(f"📝 Raw Text Found:\n{full_text}\n{'-'*20}")

        # 5. PARSE THE DATA (THE HARD PART) 🕵️‍♂️
        # Since Google doesn't know what a 'Total' is, we have to find it ourselves.
        
        data = {
            "vendor": parse_vendor(texts),     # Guess the store name
            "date": parse_date(full_text),     # Find a date pattern
            "total": parse_total(full_text),   # Find the biggest money number
            "category": "Uncategorized"        # Google won't tell us this :(
        }
        
        return data

    except Exception as e:
        print(f"❌ Google Vision Error: {e}")
        return None


# --- HELPER FUNCTIONS (THE "BRAIN") ---

def parse_vendor(texts):
    """
    Simple logic: The vendor is usually the text at the very top of the receipt.
    """
    try:
        # texts[0] is the whole block, texts[1] is the first word/line found.
        # We might grab the first valid line that isn't a number.
        lines = texts[0].description.split('\n')
        if lines:
            return lines[0].strip() # First line is usually the store name (e.g., "Walmart")
        return "Unknown Vendor"
    except:
        return None

def parse_date(text):
    """
    Regex to find dates like 12/05/2025, 2025-05-12, or Dec 05, 2025.
    """
    # Regex for MM/DD/YYYY or DD/MM/YYYY or YYYY-MM-DD
    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
    match = re.search(date_pattern, text)
    if match:
        return match.group(0)
    return None

def parse_total(text):
    """
    Finds the word 'Total' (or 'Amount') and looks for the number next to it.
    If that fails, it finds the largest number in the text with a decimal.
    """
    # 1. Try to find "Total: $25.00"
    total_pattern = r'(?i)(total|balance|amount|due)[\s:$]*(\d{1,5}\.\d{2})'
    match = re.search(total_pattern, text)
    if match:
        return match.group(2) # The number part

    # 2. Fallback: Find ALL money-looking numbers (e.g., 12.99) and take the biggest one.
    # This is a hack, but it works 80% of the time for receipts.
    money_pattern = r'\b\d{1,5}\.\d{2}\b'
    amounts = re.findall(money_pattern, text)
    
    if amounts:
        # Convert strings to floats to compare
        valid_amounts = [float(a) for a in amounts]
        return max(valid_amounts) # Return the largest amount found
        
    return None
