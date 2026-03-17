# Запуск и тестирование

## Требования

- Docker и Docker Compose

## Быстрый запуск

```bash
cd 02_transaction_manager_django
cp .env.example .env
docker compose up --build -d
```

## Доступные сервисы

| Сервис | URL |
|--------|-----|
| API | http://localhost:8000/api/ |
| Admin | http://localhost:8000/admin/ |
| Grafana | http://localhost:3000 (admin/admin) |

## Для доступа в админку Djando нужно создать superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## Запуск тестов

```bash
docker compose run --rm web python manage.py test
```

## Примеры запросов

### Создание транзакции
```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{"user_id": 1, "amount": 100.00, "type": "deposit"}'
```

### Оплата через PayPal
```bash
curl -X POST http://localhost:8000/api/paypal/create/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 1}'
```

### Webhook PayPal
```bash
curl -X POST http://localhost:8000/api/paypal/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"event_type": "PAYMENT.CAPTURE.COMPLETED", "payment_id": "PAY-XXX", "status": "completed"}'
```

## Просмотр логов

В Grafana (http://localhost:3000): Explore → Loki → `{job="web"}`

## Остановка

```bash
docker compose down -v
```
