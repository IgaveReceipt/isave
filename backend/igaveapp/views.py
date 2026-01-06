import os
import tempfile
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework import viewsets, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

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

    # Allow JSONParser so we can send text edits
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'date', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='scan')
    def analyze_receipt(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {"error": "No file provided. Send 'file' as form-data."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            print(f"Analyzing: {uploaded_file.name}...")
            data = extract_receipt_data(temp_file_path)

            if not data:
                return Response(
                    {"error": "OCR failed to read the receipt."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            draft_data = {
                "store_name": data.get('vendor') or "Unknown Vendor",
                "date": data.get('date'),
                "total_amount": data.get('total'),
                "items": data.get('items', []),
                "category": data.get('category'),
                "status": "pending"
            }

            print(f"✅ Analysis Complete. Draft Category: {draft_data['category']}")
            return Response(draft_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ Error in analyze_receipt: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # --- THE ACCOUNTANT V2 (With Time Filters) ---
    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        """
        Endpoint: GET /api/receipts/stats/?month=1&year=2026
        """
        queryset = self.get_queryset()

        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)
        elif year:
            queryset = queryset.filter(date__year=year)

        stats = queryset.values('category').annotate(total=Sum('total_amount')).order_by('-total')

        labels = []
        values = []
        grand_total = 0

        for entry in stats:
            cat_name = entry['category']
            if cat_name:
                cat_name = cat_name.capitalize()
            else:
                cat_name = "Uncategorized"

            amount = entry['total'] or 0

            labels.append(cat_name)
            values.append(amount)
            grand_total += amount

        return Response({
            "labels": labels,
            "data": values,
            "total_spent": grand_total,
            "filter": f"Month: {month}, Year: {year}" if month else "All Time"
        })
