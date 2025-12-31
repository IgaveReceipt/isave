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
    """
    client = None

    # --- 1. SETUP GOOGLE CLIENT 🤖 ---
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
                print("❌ OCR Error: No Google Credentials found.")
                return None
    except Exception as e:
        print(f"❌ OCR Client Setup Error: {e}")
        return None

    # --- 2. CALL VISION API 👁️ ---
    try:
        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        # We use text_detection to get the full block of text
        response = client.text_detection(image=image)
        
        if not response.text_annotations:
            print("⚠️ OCR: No text found in image.")
            return None

        # The first annotation contains the entire text
        full_text = response.text_annotations[0].description
        lines = full_text.split('\n')
        
    except Exception as e:
        print(f"❌ OCR Processing Error: {e}")
        return None

    # --- 3. SMART EXTRACTION LOGIC 🧠 ---
    
    data = {
        "vendor": None,
        "date": None,
        "total": None,
        "items": [] 
    }

    # Regex Patterns
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\.\d{1,2}\.\d{2,4}|\d{4}-\d{2}-\d{2})'
    total_pattern = r'(?i)(total|amount|balance|due|grand total)\s*[:$]?\s*(\d+[.,]\d{2})'
    
    # NEW: Item Pattern (Text followed by a price at the end of the line)
    # Looks for: "Cheese Burger   10.50" or "Coffee 4,50"
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

    # ... (Keep Sections A, B, and C the same) ...

    # --- D. EXECUTE ITEM SEARCH (THE MATCHMAKER FIX) 💘 ---
    print("\n🐢 --- DEBUG: MATCHMAKER MODE ---")
    
    # Pattern 1: One Line (Text ... Price)
    # e.g. "Burger 10.50"
    single_line_pattern = r'(.+?)\s+[$]?(\d+[.,]\d{2})$'

    # Pattern 2: Price Line (Just a price)
    # e.g. "$10.50" or "10.50"
    price_only_pattern = r'^[$]?\s*(\d+[.,]\d{2})$'

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip garbage
        if not line:
            i += 1
            continue

        print(f"Line {i}: '{line}'", end=" ... ")

        # --- CHECK 1: Is it a "Single Line" Item? ---
        # (e.g. "Burger 10.50")
        match = re.search(single_line_pattern, line)
        if match:
            item_name = match.group(1).strip()
            item_price = match.group(2).replace(',', '.')
            
            # Validation
            if any(bad in item_name.lower() for bad in blacklist_words):
                print("❌ Ignored (Blacklist)")
            elif data['date'] and data['date'] in item_name:
                print("❌ Ignored (Date)")
            else:
                print(f"✅ MATCH (Single Line)! {item_name} -> {item_price}")
                data['items'].append({"name": item_name, "price": float(item_price)})
            
            i += 1
            continue

        # --- CHECK 2: Is it a "Split Line" Item? ---
        # (Current line is Name, NEXT line is Price)
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            price_match = re.match(price_only_pattern, next_line)
            
            if price_match:
                # We found a potential match!
                item_name = line
                item_price = price_match.group(1).replace(',', '.')
                
                # Validation
                if any(bad in item_name.lower() for bad in blacklist_words):
                    print("❌ Ignored (Blacklist) - skipping next line too")
                elif re.match(r'^[\d\W]+$', item_name): 
                    # If name is just numbers/symbols (like "1"), ignore it
                    print("❌ Ignored (Just Numbers)")
                    # NOTE: We do NOT skip the next line here, because "1" might be quantity 
                    # and the REAL item might be on the next line.
                    i += 1
                    continue 
                else:
                    print(f"✅ MATCH (Split Line)! {item_name} -> {item_price}")
                    data['items'].append({"name": item_name, "price": float(item_price)})
                    i += 2 # Skip BOTH lines (Name and Price)
                    continue

        print("❌ No match")
        i += 1

    print("🐢 --- END DEBUG ---\n")

    return data