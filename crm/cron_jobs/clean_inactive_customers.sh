#!/bin/bash

cd /home/gem_geek/projects/alx-backend-graphql_crm

source venv/bin/activate

PY_CMD="from django.utils import timezone; from datetime import timedelta; from crm.models import Customer; from django.db.models import Max, Q; one_year_ago = timezone.now() - timedelta(days=365); customers_to_delete = Customer.objects.annotate(latest_order=Max('order__created_at')).filter(Q(latest_order__lt=one_year_ago) | Q(latest_order__isnull=True)); count, _ = customers_to_delete.delete(); print(count)"

COUNT=$(python manage.py shell -c "$PY_CMD")

echo "$(date '+%Y-%m-%d %H:%M:%S'): Deleted $COUNT inactive customers." >> /tmp/customer_cleanup_log.txt