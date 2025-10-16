import os
import django
from django.utils import timezone
from decimal import Decimal

# Set up the Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    print("--- Deleting old data... ---")
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    print("--- Seeding new data... ---")
    
    # Create Customers
    customer1 = Customer.objects.create(name="John Doe", email="john.doe@example.com", phone="+15551234567")
    customer2 = Customer.objects.create(name="Jane Smith", email="jane.smith@example.com")
    
    # Create Products
    product1 = Product.objects.create(name="Laptop Pro", price=Decimal("1200.00"), stock=50)
    product2 = Product.objects.create(name="Wireless Mouse", price=Decimal("25.50"), stock=200)
    product3 = Product.objects.create(name="Mechanical Keyboard", price=Decimal("75.00"), stock=100)
    
    # Create an Order
    order1 = Order.objects.create(customer=customer1, total_amount=product1.price + product2.price)
    order1.products.set([product1, product2])
    
    print("--- Seeding complete! ---")
    print(f"Created {Customer.objects.count()} customers.")
    print(f"Created {Product.objects.count()} products.")
    print(f"Created {Order.objects.count()} orders.")

# Run the seeding function
if __name__ == "__main__":
    seed_database()