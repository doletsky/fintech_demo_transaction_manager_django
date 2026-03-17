# Launch and Testing

## Requirements

- Docker and Docker Compose

## Quick Start

```bash
cd 02_transaction_manager_django
cp .env.example .env
docker compose up --build -d
```

## Available Services

| Service | URL |
|---------|-----|
| API     | http://localhost:8000/api/ |
| Admin   | http://localhost:8000/admin/ |
| Grafana | http://localhost:3000 (admin/admin) |

## To access Django admin, you need to create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## Running Tests

```bash
docker compose run --rm web python manage.py test
```

## Example Requests

### Create Transaction
```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{"user_id": 1, "amount": 100.00, "type": "deposit"}'
```

### Pay via PayPal
```bash
curl -X POST http://localhost:8000/api/paypal/create/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 1}'
```

### PayPal Webhook
```bash
curl -X POST http://localhost:8000/api/paypal/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"event_type": "PAYMENT.CAPTURE.COMPLETED", "payment_id": "PAY-XXX", "status": "completed"}'
```
