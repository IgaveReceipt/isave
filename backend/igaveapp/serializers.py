from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Receipt


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ReceiptSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Receipt
        fields = [
            'id', 
            'user', 
            'store_name', 
            'date', 
            'total_amount', 
            'category', 
            'items', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
