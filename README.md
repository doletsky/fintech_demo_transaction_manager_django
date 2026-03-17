# Financial Transaction Manager

A monolithic application for managing users' financial transactions based on **Django + DRF**, **MySQL**, **Celery**, with a mock PayPal service and observability stack **Grafana Loki**.

## Features

- CRUD transactions (user_id, amount, type: deposit/withdrawal/payment, status, timestamp)
- Idempotency via idempotency keys
- Transaction deduplication
- Audit log of all operations
- Celery background tasks (transaction confirmation, notifications)
- Mock PayPal service (create, confirm, webhook handling)
- Django ORM with DB transactions for consistency
- JSON logging to stdout (including Celery)
- Centralized logging: Loki + Promtail + Grafana
- Docker + docker-compose (web, db, celery_worker, redis, loki, promtail, grafana)

## Technology Stack

| Component | Technology                |
|-----------|--------------------------|
| Backend   | Django 5.x + DRF         |
| Database  | MySQL 8                  |
| Queues    | Celery + Redis           |
| Logging   | python-json-logger → stdout |
| Log Collector | Promtail → Loki      |
| Visualization | Grafana              |
| Containerization | Docker + docker-compose |
