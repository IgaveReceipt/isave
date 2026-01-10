import os
import io
import re
import json
from datetime import datetime 
from google.oauth2.service_account import Credentials
from google.cloud import vision

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_receipt_data(file_path):
    """
    Scans a receipt using Google Cloud Vision API.
    """
    client = None

    # --- 1. SETUP GOOGLE CLIENT ---
    try:
        google_json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if google_json_str:
            creds_dict = json.loads(google_json_str)
            credentials = Credentials.from_service_account_info(creds_dict)
            client = vision.ImageAnnotatorClient(credentials=credentials)
        else:
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
        response = client.text_detection(image=image)
        
        if not response.text_annotations:
            print(" OCR: No text found in image.")
            return None

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
        "category": "general",
        "items": [] 
    }

    # Regex Patterns
    date_pattern = r'(?i)(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.,-]+\d{1,2}[a-z]{0,2}[\s.,-]+\d{2,4}|\d{1,2}[\s.,-]+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.,-]+\d{2,4})'
    
    total_pattern = r'(?i)(total|amount|balance|due|grand total)\s*[:$]?\s*(\d+[.,]\d{2})'
    
    # BLACKLIST: Words that mean "User Paid Money"
    payment_blacklist = ["cash", "tender", "tendered", "change", "paid", "visa", "mastercard", "amex", "card"]

    # Words to ignore when looking for ITEMS
    blacklist_words = ["total", "subtotal", "tax", "vat", "due", "balance", "date"] + payment_blacklist

    # --- A. EXECUTE DATE SEARCH ---
    date_matches = re.findall(date_pattern, full_text)
    if date_matches:
        raw_date = date_matches[0]
        clean_date = re.sub(r'(st|nd|rd|th|,)', '', raw_date).strip()
        formats_to_try = [
            "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y", "%Y-%m-%d", 
            "%b %d %Y", "%B %d %Y", "%d %b %Y", "%d %B %Y", "%m/%d/%y", "%m-%d-%y"
        ]
        for fmt in formats_to_try:
            try:
                dt_obj = datetime.strptime(clean_date, fmt)
                data['date'] = dt_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        if not data['date']: data['date'] = raw_date

    # --- B. EXECUTE VENDOR SEARCH ---
    ignored_vendor_words = ["welcome", "receipt", "copy", "customer", "transaction", "original", "date"]
    for line in lines[:6]:
        clean_line = line.strip()
        if not clean_line or len(clean_line) < 2: continue
        if re.search(date_pattern, clean_line): continue
        if any(word in clean_line.lower() for word in ignored_vendor_words): continue
        if re.search(r'\d{3}[-.]\d{3}[-.]\d{4}', clean_line): continue 
        if re.match(r'^\$?\d+[.,]\d{2}$', clean_line): continue 
        data['vendor'] = clean_line
        break 
    if not data['vendor']: data['vendor'] = "Unknown Vendor"

    # --- C. EXECUTE TOTAL SEARCH (The "Pre-Filter" Fix) ---
    
    # 1. Create a SAFE list of lines (Remove all payment noise FIRST)
    safe_lines = []
    skip_next_line = False
    
    for i, line in enumerate(lines):
        if skip_next_line:
            skip_next_line = False
            continue
            
        lower_line = line.lower()
        
        # Check if this is a "Payment" line
        if any(bad in lower_line for bad in payment_blacklist):
            # It's bad! Now check if it's a "Split Line" trap.
            # Does this line have a price on it?
            has_price = re.search(r'\d+[.,]\d{2}', line)
            
            if not has_price:
                # No price here? It must be on the NEXT line. Poison it!
                skip_next_line = True
            
            # Skip THIS line regardless
            continue
        
        # If we survived, add to safe list
        safe_lines.append(line)

    # 2. Search for Total in the SAFE lines only
    # Strict Match first
    for line in safe_lines:
        match = re.search(total_pattern, line)
        if match:
             data['total'] = match.group(2).replace(',', '.')
             break
        
    # 3. Fallback: Max number from SAFE lines
    if not data['total']:
        potential_totals = []
        for line in safe_lines:
            prices = re.findall(r'\$?\s*(\d+[.,]\d{2})', line)
            for p in prices:
                try:
                    floats = float(p.replace(',', '.'))
                    potential_totals.append(floats)
                except: pass

        if potential_totals:
            data['total'] = str(max(potential_totals))


    # --- D. EXECUTE ITEM SEARCH ---
    print("\n --- DEBUG: MATCHMAKER MODE ---")
    single_line_pattern = r'(.+?)\s+[$]?(\d+[.,]\d{2})$'
    price_only_pattern = r'^[$]?\s*(\d+[.,]\d{2})$'

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        match = re.search(single_line_pattern, line)
        if match:
            item_name = match.group(1).strip()
            item_price = match.group(2).replace(',', '.')
            
            if any(bad in item_name.lower() for bad in blacklist_words):
                pass
            elif data['date'] and data['date'] in item_name:
                pass
            else:
                data['items'].append({"name": item_name, "price": float(item_price)})
            i += 1
            continue

        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            price_match = re.match(price_only_pattern, next_line)
            if price_match:
                item_name = line
                item_price = price_match.group(1).replace(',', '.')
                
                if any(bad in item_name.lower() for bad in blacklist_words):
                    pass
                elif re.match(r'^[\d\W]+$', item_name): 
                    i += 1
                    continue 
                else:
                    data['items'].append({"name": item_name, "price": float(item_price)})
                    i += 2 
                    continue
        i += 1

    # --- E. CATEGORIZATION ---
    categories = {
        'food': ['burger', 'pizza', 'restaurant', 'cafe', 'coffee', 'grill', 'kitchen', 'food', 'market', 'diner', 'bistro', 'steak', 'mcdonalds', 'kfc', 'starbucks', 'subway', 'wendys', 'taco bell', 'dunkin', 'chipotle', 'domino', 'meal', 'bread', 'bakery', 'sushi'],
        'transport': ['uber', 'lyft', 'taxi', 'shell', 'exxon', 'bp', 'chevron', 'fuel', 'gas', 'station', 'train', 'metro', 'bus', 'airline', 'flight', 'parking', 'garage'],
        'utilities': ['water', 'electric', 'power', 'energy', 'internet', 'wifi', 'telecom', 'mobile', 'at&t', 'verizon', 't-mobile', 'comcast', 'bill', 'insurance'],
        'shopping': ['amazon', 'walmart', 'target', 'ikea', 'mall', 'shop', 'clothing', 'shoes', 'apparel', 'nike', 'adidas', 'zara', 'h&m', 'retail', 'outlet', 'boutique', 'book'],
        'entertainment': ['cinema', 'movie', 'theatre', 'netflix', 'spotify', 'ticket', 'event', 'bowling', 'golf', 'game', 'concert', 'museum'],
        'health': ['pharmacy', 'cvs', 'walgreens', 'hospital', 'clinic', 'doctor', 'dental', 'gym', 'fitness', 'medicine', 'drug']
    }

    def check_category(text):
        if not text: return None
        text = text.lower()
        for cat, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return cat
        return None

    cat_match = check_category(data['vendor'])
    if not cat_match:
        for item in data['items'][:5]:
            cat_match = check_category(item['name'])
            if cat_match: break
    if cat_match:
        data['category'] = cat_match

    return data