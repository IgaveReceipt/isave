import os
import tempfile
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Receipt
from .serializers import UserSerializer, ReceiptSerializer
from .ocr import extract_receipt_data  # Import our OCR brain


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

    # 1. Allow this view to accept file uploads (Images)
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        # Only show receipts that belong to the logged-in user
        return Receipt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # When creating manually, auto-assign the user
        serializer.save(user=self.request.user)

    # --- THE NEW BRIDGE ---
    @action(detail=False, methods=['post'], url_path='scan')
    def scan_receipt(self, request):
        """
        Endpoint: POST /api/receipts/scan/
        Receives: 'file' (Image)
        Returns: The created Receipt object with OCR data
        """
        # A. Check if file exists
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {"error": "No file provided. Send 'file' as form-data."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # B. Save to a temporary file (so OCR can read it)
        # delete=False means we manually delete it later
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # C. Run the OCR Brain 🧠
            print(f"Scanning: {uploaded_file.name}...")
            data = extract_receipt_data(temp_file_path)

            if not data:
                return Response(
                    {"error": "OCR failed to read the receipt."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # D. Save to Postgres Database 💾
            receipt = Receipt.objects.create(
                user=request.user,
                store_name=data.get('vendor') or "Unknown Vendor",
                date=data.get('date'),          # OCR returns YYYY-MM-DD or None
                total_amount=data.get('total'),  # OCR returns "25.50" or None
                status='pending',               # Default status
                items=data.get('items', [])     # Empty list for now
            )

            print(f"✅ Saved Receipt: {receipt.store_name} - ${receipt.total_amount}")

            # E. Return the saved data to the Frontend
            serializer = self.get_serializer(receipt)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"❌ Error in scan_receipt: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # F. Cleanup: Delete the temp file! 🧹
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
