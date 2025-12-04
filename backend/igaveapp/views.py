from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Receipt
from .serializers import UserSerializer, ReceiptSerializer


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
