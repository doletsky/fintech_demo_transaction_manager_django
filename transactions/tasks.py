import logging
import time
from celery import shared_task

logger = logging.getLogger("transactions")


@shared_task
def confirm_transaction(transaction_id):
    from .models import Transaction, AuditLog

    time.sleep(2)  # Simulate processing delay

    try:
        tx = Transaction.objects.get(id=transaction_id)
        if tx.status == "pending":
            old_status = tx.status
            tx.status = "completed"
            tx.save()
            AuditLog.objects.create(
                transaction=tx,
                action="auto_confirmed",
                old_status=old_status,
                new_status="completed",
            )
            logger.info("Transaction auto-confirmed", extra={
                "transaction_id": tx.id, "user_id": tx.user_id,
            })
    except Transaction.DoesNotExist:
        logger.error("Transaction not found for confirmation", extra={
            "transaction_id": transaction_id,
        })


@shared_task
def send_notification(transaction_id, message):
    logger.info("Notification sent", extra={
        "transaction_id": transaction_id, "message": message,
    })
