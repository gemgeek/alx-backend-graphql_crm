from celery import shared_task
from datetime import datetime  
import requests                
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

TRANSPORT = RequestsHTTPTransport(url="http://localhost:8000/graphql")
GQL_CLIENT = Client(transport=TRANSPORT, fetch_schema_from_transport=False)

LOG_FILE = "/tmp/crm_report_log.txt"

logger = logging.getLogger(__name__)

REPORT_QUERY = gql("""
    query CrmReport {
      totalCustomers
      totalOrders
      totalRevenue
    }
""")

@shared_task
def generate_crm_report():
    """
    A Celery task to generate a weekly CRM report and log it to a file.
    """
    logger.info("Starting crm report task...")

    try:
        result = GQL_CLIENT.execute(REPORT_QUERY)

        customers = result.get('totalCustomers', 'N/A')
        orders = result.get('totalOrders', 'N/A')
        revenue = result.get('totalRevenue', 'N/A')

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_message = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue.\n"

        with open(LOG_FILE, "a") as f:
            f.write(log_message)

        logger.info("CRM report generated successfully.")
        return log_message

    except Exception as e:
        logger.error(f"Error generating CRM report: {e}")
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {e}\n")
        except IOError:
            pass 
        return f"Error: {e}"