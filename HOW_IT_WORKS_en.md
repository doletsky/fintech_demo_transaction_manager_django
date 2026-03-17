# How the Project Works

## General Idea

This is a system for managing financial transactions—deposits, withdrawals, and payments. Each transaction goes through a lifecycle (created → processing → confirmed/rejected), and everything is recorded in the audit log.

## How It's Built

### 1. REST API (Django + DRF)
The app provides an API for working with transactions. Django REST Framework (DRF) automatically handles data serialization, validation, and response formatting.

### 2. Idempotency
If the same request is sent twice (for example, due to network issues), the system will not create a duplicate. For this, an `Idempotency-Key` is used—a unique key in the request header. If the key was already used, the result of the previous request is returned.

### 3. Audit Log
Every transaction change is recorded in a separate audit table: who, when, and what was done. This allows you to track the entire history of changes.

### 4. Background Tasks (Celery)
Some operations are performed in the background so the user doesn't have to wait:
- **Transaction confirmation** — a few seconds after creation, the transaction is automatically confirmed
- **Notifications** — sending notifications about transaction status

Celery uses Redis as a message broker—it passes tasks from the API to the worker.

### 5. Mock PayPal
PayPal emulation for payments:
- **create** — creates a payment linked to a transaction
- **capture** — confirms the withdrawal
- **webhook** — PayPal "notifies" the system about successful payment, transaction status changes to "completed"

### 6. Logging and Monitoring
All actions are logged in JSON format: transaction creation, status change, errors. Logs are collected by Promtail and sent to Loki. In Grafana, you can search logs by transaction_id, user_id, payment_status.

### 7. Docker
All components run in containers:
- **web** — Django app
- **db** — MySQL
- **celery_worker** — background task worker
- **redis** — broker for Celery
- **loki + promtail + grafana** — logging stack

## Data Flow

```
User → API (DRF) → Transaction in MySQL
                   ↓                    ↓
              Audit log          Celery task → Redis → Worker → confirmation
                   ↓
              Mock PayPal (create → capture → webhook)
                   ↓
              JSON logs → Promtail → Loki → Grafana
```
