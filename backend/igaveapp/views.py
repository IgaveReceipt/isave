from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.conf import settings
from .models import Receipt
from .serializers import UserSerializer, ReceiptSerializer
from .ocr import extract_receipt_data
import os

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ReceiptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing receipts.
    """
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return receipts for the current user only."""
        return Receipt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user to the current user when creating a receipt."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def scan(self, request):
        """
        Receives an image, saves it temporarily, scans it with Mindee, 
        and returns the data (Vendor, Date, Total).
        """
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            return Response(
                {"error": "No file uploaded. Please send a 'file' key."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


        temp_dir = os.path.join(settings.BASE_DIR, 'tmp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        full_path = os.path.join(temp_dir, uploaded_file.name)

        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        try:
            data = extract_receipt_data(full_path)
            if not data:
                return Response(
                    {"error": "OCR failed to read the document."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(data)

        finally:
            if os.path.exists(full_path):
                os.remove(full_path)