import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    # Challenge: Custom filter method for phone number patterns
    phone_starts_with = django_filters.CharFilter(method='filter_phone_starts_with', label="Phone starts with")

    class Meta:
        model = Customer
        # Define filters for name (case-insensitive contains), email (icontains), and date ranges
        fields = {
            'name': ['icontains'],
            'email': ['icontains'],
            'created_at': ['gte', 'lte'], # gte = greater than or equal to, lte = less than or equal to
        }

    def filter_phone_starts_with(self, queryset, name, value):
        # This custom function is called when the 'phone_starts_with' filter is used
        return queryset.filter(phone__startswith=value)

class ProductFilter(django_filters.FilterSet):
    # Challenge: Custom filter for low stock
    low_stock = django_filters.BooleanFilter(method='filter_low_stock', label="Is low stock?")

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }

    def filter_low_stock(self, queryset, name, value):
        # If the filter is used and is true, return products with stock < 10
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

class OrderFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')

    # Challenge: Custom filter for a specific product ID
    has_product_id = django_filters.NumberFilter(method='filter_has_product_id', label="Contains Product ID")

    class Meta:
        model = Order
        fields = {
            'total_amount': ['gte', 'lte'],
            'order_date': ['gte', 'lte'],
        }

    def filter_has_product_id(self, queryset, name, value):
        # Filter orders to find those that contain a product with the given ID
        return queryset.filter(products__id=value).distinct()