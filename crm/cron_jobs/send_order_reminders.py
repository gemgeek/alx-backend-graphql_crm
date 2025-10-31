#!/usr/bin/env python3

import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

TRANSPORT = RequestsHTTPTransport(url="http://localhost:8000/graphql")

CLIENT = Client(transport=TRANSPORT, fetch_schema_from_transport=False)

LOG_FILE = "/tmp/order_reminders_log.txt"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

GET_RECENT_ORDERS_QUERY = gql("""
    query GetRecentOrders($date_7_days_ago: DateTime!) {
      orders(orderDate_Gte: $date_7_days_ago) {
        id
        customer {
          email
        }
      }
    }
""")

def fetch_and_log_reminders():
    try:
        date_7_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

        params = {"date_7_days_ago": date_7_days_ago}

        result = CLIENT.execute(GET_RECENT_ORDERS_QUERY, variable_values=params)

        if result and 'orders' in result:
            orders = result['orders']
            if not orders:
                logging.info("No recent orders found.")
            else:
                logging.info(f"Found {len(orders)} recent orders. Sending reminders...")
                for order in orders:
                    logging.info(f"  - Order ID: {order['id']}, Customer: {order['customer']['email']}")
        else:
            logging.warning("Query executed, but no 'orders' key in result.")

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error fetching order reminders: {e}")
        print(f"Error: {e}") 

if __name__ == "__main__":
    fetch_and_log_reminders()