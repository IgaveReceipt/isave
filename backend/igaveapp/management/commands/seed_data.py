import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from igaveapp.models import Receipt

class Command(BaseCommand):
    help = 'Injects fake receipt data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username to assign receipts to')
        parser.add_argument('--count', type=int, default=20, help='Number of receipts to create')

    def handle(self, *args, **options):
        username = options['username']
        count = options['count']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User '{username}' not found! Please create them first."))
            return

        # The Data Pool 
        stores = [
            "Walmart", "Target", "Starbucks", "Shell Station", "Uber Rides", 
            "Netflix", "Apple Store", "Trader Joe's", "Amazon", "CVS Pharmacy", 
            "McDonald's", "Whole Foods", "Spotify", "Gym Membership", "7-Eleven"
        ]
        
        # Matches your CATEGORY_CHOICES in models.py
        categories = ['food', 'transport', 'utilities', 'shopping', 'entertainment', 'health', 'general']
        
        self.stdout.write(f"🌱 Seeding {count} receipts for {username}...")

        for i in range(count):
            # 1. Random Date (Last 3 months)
            days_ago = random.randint(0, 90)
            fake_date = date.today() - timedelta(days=days_ago)

            # 2. Random Amount ($5.00 to $180.00)
            fake_amount = round(random.uniform(5.00, 180.00), 2)
            
            # 3. Random Store & Category
            store = random.choice(stores)
            cat = random.choice(categories)

            # 4. Create the Receipt
            Receipt.objects.create(
                user=user,
                store_name=store,
                date=fake_date,
                total_amount=fake_amount,
                category=cat,
                # Mix of Verified/Pending so the chart looks interesting
                status=random.choice(['verified', 'verified', 'verified', 'pending']), 
                items=[
                    {"desc": "Demo Item 1", "price": round(fake_amount * 0.6, 2)},
                    {"desc": "Tax", "price": round(fake_amount * 0.4, 2)}
                ] 
            )

        self.stdout.write(self.style.SUCCESS(f" Successfully added {count} fake receipts for {username}!"))