import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
import re
from django.db import IntegrityError, transaction


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# --- Root Query ---

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)

    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)

    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)


# --- Mutations ---

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    # Output fields
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, name, email, phone=None):
        # Phone number validation 
        if phone and not re.match(r'^(\+?[1-9]\d{1,14}|(\d{3}-){2}\d{4})$', phone):
            raise Exception("Invalid phone number format. Use +1234567890 or 123-456-7890.")

        try:
            customer = Customer.objects.create(name=name, email=email, phone=phone)
            return CreateCustomer(customer=customer, message="Customer created successfully!")
        except IntegrityError:
            raise Exception("Email already exists. Please use a different email.")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers_data = graphene.List(graphene.NonNull(CustomerInput), required=True)

    # Output fields
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, customers_data):
        successful_customers = []
        error_messages = []

        # Use a transaction to ensure atomicity if needed, though we want partial success
        for i, customer_data in enumerate(customers_data):
            try:
                # Validate phone
                if customer_data.phone and not re.match(r'^(\+?[1-9]\d{1,14}|(\d{3}-){2}\d{4})$', customer_data.phone):
                    raise ValueError(f"Record {i+1}: Invalid phone number format.")

                # Check for existing email manually for bulk operation
                if Customer.objects.filter(email=customer_data.email).exists():
                     raise ValueError(f"Record {i+1}: Email '{customer_data.email}' already exists.")

                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone
                )
                successful_customers.append(customer)
            except ValueError as e:
                error_messages.append(str(e))

        # Use bulk_create for efficiency
        if successful_customers:
            Customer.objects.bulk_create(successful_customers)

        return BulkCreateCustomers(customers=successful_customers, errors=error_messages)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be a positive number.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        if not product_ids:
            raise Exception("At least one product must be selected.")

        products = Product.objects.filter(pk__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more product IDs are invalid.")

        total_amount = sum(product.price for product in products)

        with transaction.atomic():
            order = Order.objects.create(customer=customer, total_amount=total_amount)
            if order_date:
                order.order_date = order_date

            order.products.set(products)
            order.save()

        return CreateOrder(order=order)


# --- Root Mutation ---

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()