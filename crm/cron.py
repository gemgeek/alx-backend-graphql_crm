import datetime

def log_crm_heartbeat():
    """
    A cron job function to log a heartbeat message, confirming
    the application is alive and cron is running.
    """
    now = datetime.datetime.now()

    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")

    log_message = f"{timestamp} CRM is alive\n" 

    try:
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(log_message)

        print(f"Logged heartbeat: {log_message.strip()}")

    except IOError as e:
        print(f"Error writing to heartbeat log: {e}")