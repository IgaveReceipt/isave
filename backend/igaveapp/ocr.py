import os
import io
import re
import json
from google.oauth2.service_account import Credentials
from google.cloud import vision

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_receipt_data(file_path):
    """
    Scans a receipt using Google Cloud Vision API and intelligently extracts:
    - Vendor (Store Name)
    - Date (US & EU formats)
    - Total Amount
    - Category (Food, Transport, etc.)
    """
    client = None

    # --- 1. SETUP GOOGLE CLIENT ---
    try:
        # Check environment variable first (Production / Secure)
        google_json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")

        if google_json_str:
            creds_dict = json.loads(google_json_str)
            credentials = Credentials.from_service_account_info(creds_dict)
            client = vision.ImageAnnotatorClient(credentials=credentials)
        else:
            # Check local file (Development)
            creds_path = os.path.join(BASE_DIR, "google_credentials.json")
            if os.path.exists(creds_path):
                client = vision.ImageAnnotatorClient.from_service_account_json(creds_path)
            else:
                print(" OCR Error: No Google Credentials found.")
                return None
    except Exception as e:
        print(f" OCR Client Setup Error: {e}")
        return None

    # --- 2. CALL VISION API  ---
    try:
        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        # We use text_detection to get the full block of text
        response = client.text_detection(image=image)
        
        if not response.text_annotations:
            print(" OCR: No text found in image.")
            return None

        # The first annotation contains the entire text
        full_text = response.text_annotations[0].description
        lines = full_text.split('\n')
        
    except Exception as e:
        print(f" OCR Processing Error: {e}")
        return None

    # --- 3. SMART EXTRACTION LOGIC  ---
    
    data = {
        "vendor": None,
        "date": None,
        "total": None,
        "category": "general", # Default value
        "items": [] 
    }

    # Regex Patterns
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\.\d{1,2}\.\d{2,4}|\d{4}-\d{2}-\d{2})'
    total_pattern = r'(?i)(total|amount|balance|due|grand total)\s*[:$]?\s*(\d+[.,]\d{2})'
    
    # NEW: Item Pattern (Text followed by a price at the end of the line)
    item_pattern = r'(.+?)\s+(\d+[.,]\d{2})$'

    # Words to ignore when looking for items
    blacklist_words = ["total", "subtotal", "tax", "vat", "change", "cash", "due", "balance", "visa", "mastercard", "date"]

    # --- A. EXECUTE DATE SEARCH ---
    date_matches = re.findall(date_pattern, full_text)
    if date_matches:
        data['date'] = date_matches[0]

    # --- B. EXECUTE VENDOR SEARCH ---
    ignored_vendor_words = ["welcome", "receipt", "copy", "customer", "transaction", "original", "date"]
    for line in lines[:6]:
        clean_line = line.strip()
        if not clean_line or len(clean_line) < 2: continue
        if re.search(date_pattern, clean_line): continue
        if any(word in clean_line.lower() for word in ignored_vendor_words): continue
        if re.search(r'\d{3}[-.]\d{3}[-.]\d{4}', clean_line): continue # Phone numbers
        if re.match(r'^\$?\d+[.,]\d{2}$', clean_line): continue # Standalone prices
        
        data['vendor'] = clean_line
        break 
    if not data['vendor']: data['vendor'] = "Unknown Vendor"

    # --- C. EXECUTE TOTAL SEARCH ---
    total_match = re.search(total_pattern, full_text)
    if total_match:
        data['total'] = total_match.group(2).replace(',', '.')
    else:
        # Fallback max number
        all_prices = re.findall(r'\$?\s*(\d+\.\d{2})', full_text)
        if all_prices:
            try:
                floats = [float(p) for p in all_prices]
                data['total'] = str(max(floats))
            except: pass

    # --- D. EXECUTE ITEM SEARCH (THE MATCHMAKER FIX)  ---
    print("\n --- DEBUG: MATCHMAKER MODE ---")
    
    single_line_pattern = r'(.+?)\s+[$]?(\d+[.,]\d{2})$'
    price_only_pattern = r'^[$]?\s*(\d+[.,]\d{2})$'

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        print(f"Line {i}: '{line}'", end=" ... ")

        # Check 1: Single Line Item
        match = re.search(single_line_pattern, line)
        if match:
            item_name = match.group(1).strip()
            item_price = match.group(2).replace(',', '.')
            
            if any(bad in item_name.lower() for bad in blacklist_words):
                print(" Ignored (Blacklist)")
            elif data['date'] and data['date'] in item_name:
                print(" Ignored (Date)")
            else:
                print(f" MATCH (Single Line)! {item_name} -> {item_price}")
                data['items'].append({"name": item_name, "price": float(item_price)})
            i += 1
            continue

        # Check 2: Split Line Item
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            price_match = re.match(price_only_pattern, next_line)
            
            if price_match:
                item_name = line
                item_price = price_match.group(1).replace(',', '.')
                
                if any(bad in item_name.lower() for bad in blacklist_words):
                    print(" Ignored (Blacklist)")
                elif re.match(r'^[\d\W]+$', item_name): 
                    print(" Ignored (Just Numbers)")
                    i += 1
                    continue 
                else:
                    print(f" MATCH (Split Line)! {item_name} -> {item_price}")
                    data['items'].append({"name": item_name, "price": float(item_price)})
                    i += 2 
                    continue

        print(" No match")
        i += 1

    print(" --- END DEBUG ---\n")

    # --- E. INTELLIGENT CATEGORIZATION  ---
    categories = {
        'food': [
            'burger', 'pizza', 'restaurant', 'cafe', 'coffee', 'grill', 'kitchen', 'food', 'market', 
            'diner', 'bistro', 'steak', 'mcdonalds', 'kfc', 'starbucks', 'subway', 'wendys', 'taco bell',
            'dunkin', 'chipotle', 'domino', 'meal', 'bread', 'bakery', 'sushi'
        ],
        'transport': [
            'uber', 'lyft', 'taxi', 'shell', 'exxon', 'bp', 'chevron', 'fuel', 'gas', 'station', 
            'train', 'metro', 'bus', 'airline', 'flight', 'parking', 'garage'
        ],
        'utilities': [
            'water', 'electric', 'power', 'energy', 'internet', 'wifi', 'telecom', 'mobile', 
            'at&t', 'verizon', 't-mobile', 'comcast', 'bill', 'insurance'
        ],
        'shopping': [
            'amazon', 'walmart', 'target', 'ikea', 'mall', 'shop', 'clothing', 'shoes', 'apparel',
            'nike', 'adidas', 'zara', 'h&m', 'retail', 'outlet', 'boutique', 'book'
        ],
        
        'entertainment': [
            'cinema', 'movie', 'theatre', 'netflix', 'spotify', 'ticket', 'event', 'bowling', 
            'golf', 'game', 'concert', 'museum'
        ],
        'health': [
            'pharmacy', 'cvs', 'walgreens', 'hospital', 'clinic', 'doctor', 'dental', 'gym', 
            'fitness', 'medicine', 'drug'
        ]
    }

    # Helper to check text against keywords
    def check_category(text):
        if not text: return None
        text = text.lower()
        
        # Check explicit keywords
        for cat, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return cat
        return None

    # 1. Check Vendor First (High Priority)
    cat_match = check_category(data['vendor'])
    
    # 2. If no vendor match, check the first few items
    if not cat_match:
        for item in data['items'][:5]: # Check first 5 items
            cat_match = check_category(item['name'])
            if cat_match: break
    
    if cat_match:
        data['category'] = cat_match

    return data