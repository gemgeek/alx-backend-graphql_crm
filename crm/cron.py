import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError

TRANSPORT = RequestsHTTPTransport(url="http://localhost:8000/graphql")
CLIENT = Client(transport=TRANSPORT, fetch_schema_from_transport=False)

HELLO_QUERY = gql("query { hello }")

logger = logging.getLogger(__name__)

def log_crm_heartbeat():
    """
    A cron job function to log a heartbeat message, confirming
    the application is alive and cron is running.
    
    Also checks if the GraphQL endpoint is responsive.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")
    
    gql_status = "unresponsive" 
    
    try:
        result = CLIENT.execute(HELLO_QUERY)
        if result and 'hello' in result:
            gql_status = "responsive" 
            
    except TransportQueryError as e:
        gql_status = f"error ({e})"
        logger.warning(f"GraphQL heartbeat query failed: {e}")
    except Exception as e:
        gql_status = f"down ({e})"
        logger.error(f"GraphQL heartbeat connection error: {e}")
        
    log_message = f"{timestamp} CRM is alive (GraphQL: {gql_status})\n"
    
    try:
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(log_message)
        
        print(f"Logged heartbeat: {log_message.strip()}")
        
    except IOError as e:
        print(f"Error writing to heartbeat log: {e}")


UPDATE_LOW_STOCK_MUTATION = gql("""
    mutation UpdateLowStockProducts {
      updateLowStockProducts {
        success
        updatedProducts {
          name
          stock
        }
      }
    }
""")

def update_low_stock():
    """
    Cron job to find low-stock products, restock them via
    GraphQL mutation, and log the updates.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"
    
    print(f"Running update_low_stock job at {timestamp}...")
    
    try:
        result = CLIENT.execute(UPDATE_LOW_STOCK_MUTATION)
        
        with open(log_file, "a") as f:
            f.write(f"--- Log entry: {timestamp} ---\n")
            
            if result and 'updateLowStockProducts' in result:
                data = result['updateLowStockProducts']
                
                if data['success'] and 'updatedProducts' in data:
                    products = data['updatedProducts']
                    if not products:
                        f.write("No low-stock products found to update.\n")
                        print("No low-stock products found.")
                    else:
                        f.write(f"Successfully restocked {len(products)} products:\n")
                        print(f"Successfully restocked {len(products)} products.")
                        for product in products:
                            f.write(f"  - Name: {product['name']}, New Stock: {product['stock']}\n")
                else:
                    f.write("Mutation failed or returned no success message.\n")
                    print("Mutation failed or returned no success message.")
            else:
                f.write("Error: Invalid response from GraphQL mutation.\n")
                print("Error: Invalid response from GraphQL mutation.")
        
    except Exception as e:
        error_message = f"Error running low_stock update: {e}\n"
        print(error_message)
        try:
            with open(log_file, "a") as f:
                f.write(f"--- ERROR: {timestamp} ---\n")
                f.write(error_message)
        except IOError:
            pass         