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