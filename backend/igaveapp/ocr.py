# backend/igaveapp/ocr.py
import os
from dotenv import load_dotenv
from mindee import ClientV2, PathInput, InferenceParameters

load_dotenv()

def extract_receipt_data(file_path):
    """
    Scans a receipt image using Mindee V2 and returns the data.
    """
    api_key = os.environ.get("MINDEE_API_KEY")
    model_id = os.environ.get("MINDEE_MODEL_ID")

    if not api_key or not model_id:
        print("❌ OCR Error: Missing API Key or Model ID.")
        return None

    try:
        # 1. Init Client (The V2 way that worked for you)
        client = ClientV2(api_key)
        
        # 2. Set Parameters
        params = InferenceParameters(model_id=model_id)
        
        # 3. Process the file
        input_source = PathInput(file_path)
        print(f"🚀 Scanning {file_path}...")
        
        response = client.enqueue_and_get_inference(
            input_source, 
            params
        )
        
        # 4. Extract Fields (Using the logic that finally worked!)
        # We access the .result.fields dictionary directly
        fields = response.inference.result.fields
        
        # Helper to safely get values
        def get_value(field_name):
            field = fields.get(field_name)
            return field.value if field else None

        data = {
            "vendor": get_value("supplier_name"),
            "date": get_value("date"),
            "total": get_value("total_amount"),
            "category": get_value("category")
        }
        
        return data

    except Exception as e:
        print(f"❌ Mindee Exception: {e}")
        return None

