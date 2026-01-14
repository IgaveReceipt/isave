import os
import csv
import tempfile
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework import viewsets, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Receipt
from .serializers import UserSerializer, ReceiptSerializer, CustomTokenObtainPairSerializer
from .ocr import extract_receipt_data
import datetime

# --- Custom Login View ---


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def me(self, request):
        if request.user.is_anonymous:
            return Response({"error": "Not authenticated"}, status=401)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'date', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        # Start with all receipts for the current user
        queryset = Receipt.objects.filter(user=self.request.user)

        
        # 1. Today (?today=true)
        if self.request.query_params.get('today'):
            queryset = queryset.filter(date=datetime.date.today())

        # 2. Specific Date (?date=YYYY-MM-DD)
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)

        # 3. Month (?month=YYYY-MM)
        month_param = self.request.query_params.get('month')
        if month_param:
            # We assume format is "2026-01"
            try:
                y, m = month_param.split('-')
                queryset = queryset.filter(date__year=y, date__month=m)
            except ValueError:
                pass 

        # 4. Year (?year=YYYY)
        year_param = self.request.query_params.get('year')
        if year_param:
            queryset = queryset.filter(date__year=year_param)

        # 5. Range (?start=...&end=...)
        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset

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

            print(f" Analysis Complete. Draft Category: {draft_data['category']}")
            return Response(draft_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f" Error in analyze_receipt: {e}")
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

    # --- DATA EXPORT (CSV) ---
    @action(detail=False, methods=['get'], url_path='export')
    def export_csv(self, request):
        """
        Endpoint: GET /api/receipts/export/?ids=1,2,3
        Returns: A Clean, Formatted CSV.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="iSave_Report.csv"'

        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        
        # 1. Headers
        writer.writerow(['Date', 'Store Name', 'Category', 'Amount', 'Status'])

        queryset = self.get_queryset()
        
        # Filter by IDs if provided
        ids_param = request.query_params.get('ids')
        if ids_param:
            try:
                id_list = [int(x) for x in ids_param.split(',')]
                queryset = queryset.filter(id__in=id_list)
            except ValueError:
                pass

        receipts = queryset.order_by('-date')
        
        for r in receipts:
            
            # Date: "24 Nov 2025" (Removed the comma!)
            formatted_date = r.date.strftime("%d %b %Y") if r.date else "N/A"
            
            # Money: "$30.00"
            formatted_amount = f"${r.total_amount:.2f}" if r.total_amount else "$0.00"
            
            # Status: Capitalize properly
            formatted_status = r.get_status_display() 

            # Category: Readable
            formatted_category = r.get_category_display()

            writer.writerow([
                formatted_date,
                r.store_name,
                formatted_category,
                formatted_amount,
                formatted_status
            ])

        return response
