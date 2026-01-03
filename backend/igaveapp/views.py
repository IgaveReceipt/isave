import os
import tempfile
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters  # Added filters here
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Receipt
from .serializers import UserSerializer, ReceiptSerializer
from .ocr import extract_receipt_data


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    # --- 1. ENABLE SORTING 📂 ---
    # This allows the frontend to call: /api/receipts/?ordering=-created_at
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'date', 'total_amount']
    ordering = ['-created_at']  # Default: Newest scanned first

    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # --- THE ANALYSIS BRIDGE ---
    @action(detail=False, methods=['post'], url_path='scan')
    def analyze_receipt(self, request):
        """
        Endpoint: POST /api/receipts/scan/
        Receives: 'file' (Image)
        Returns: JSON Data (Draft) - DOES NOT SAVE TO DB
        """
        # A. Check if file exists
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {"error": "No file provided. Send 'file' as form-data."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # B. Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # C. Run the OCR Brain 
            print(f"Analyzing: {uploaded_file.name}...")
            data = extract_receipt_data(temp_file_path)

            if not data:
                return Response(
                    {"error": "OCR failed to read the receipt."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # D. Construct the Draft Data
            draft_data = {
                "store_name": data.get('vendor') or "Unknown Vendor",
                "date": data.get('date'),
                "total_amount": data.get('total'),
                "items": data.get('items', []),
                
                # --- 2. PASS THE CATEGORY TO FRONTEND 🧠 ---
                "category": data.get('category'), 
                
                "status": "pending" 
            }
            
            print(f"✅ Analysis Complete. Draft Category: {draft_data['category']}")

            # E. Return the RAW data (No ID, not saved yet)
            return Response(draft_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ Error in analyze_receipt: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # F. Cleanup
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)