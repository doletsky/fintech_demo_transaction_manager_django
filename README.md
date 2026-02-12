# Менеджер финансовых транзакций

Монолитное приложение для управления финансовыми транзакциями пользователей на базе **Django + DRF**, **MySQL**, **Celery**, с мок-сервисом PayPal и observability-стеком **Grafana Loki**.

## Возможности

- CRUD транзакций (user_id, amount, type: deposit/withdrawal/payment, status, timestamp)
- Идемпотентность через idempotency keys
- Дедупликация транзакций
- Аудит-лог всех операций
- Фоновые задачи Celery (подтверждение транзакций, уведомления)
- Мок-сервис PayPal (создание, подтверждение, webhook-обработка)
- Django ORM с транзакциями БД для консистентности
- JSON-логирование в stdout (включая Celery)
- Centralized logging: Loki + Promtail + Grafana
- Docker + docker-compose (web, db, celery_worker, redis, loki, promtail, grafana)

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Backend | Django 5.x + DRF |
| БД | MySQL 8 |
| Очереди | Celery + Redis |
| Логи | python-json-logger → stdout |
| Сбор логов | Promtail → Loki |
| Визуализация | Grafana |
| Контейнеризация | Docker + docker-compose |
