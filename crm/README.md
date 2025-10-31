# Celery Setup Steps

## 1. Install Redis and Dependencies

First, ensure Redis is installed and running.

```bash
# Example on Ubuntu
sudo apt update
sudo apt install redis-server
```

Install Python dependencies:

```bash
# Assumes virtual environment is active
pip install -r requirements.txt
```

---

## 2. Run Migrations

Run Django migrations to create the Celery Beat database tables.

```bash
python manage.py migrate
```

---

## 3. Start Celery Worker

In a new terminal, start the Celery worker process.

```bash
celery -A crm worker -l info
```

---

## 4. Start Celery Beat

In a separate terminal, start the Celery Beat scheduler.

```bash
celery -A crm beat -l info
```

---

## 5. Verify Logs

You can verify the task is running by checking its log file.

```bash
tail -f /tmp/crm_report_log.txt
```