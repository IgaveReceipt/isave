from django.db import models
from django.contrib.auth.models import User


class Receipt(models.Model):

    # Define the choices for our status field
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    # Define choices for categories
    CATEGORY_CHOICES = [
        ('food', 'Food & Dining'),
        ('transport', 'Transportation'),
        ('utilities', 'Utilities'),
        ('shopping', 'Shopping'),
        ('entertainment', 'Entertainment'),
        ('health', 'Health & Fitness'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Tracks if the receipt is new or checked
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Category field with default
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='general'
    )

    # Stores the list of items (Milk, Bread, etc.) as raw JSON data
    items = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store_name} - {self.total_amount}"
