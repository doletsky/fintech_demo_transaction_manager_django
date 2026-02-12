import uuid
import logging

from django.db import transaction as db_transaction
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Transaction, AuditLog
from .serializers import TransactionSerializer, AuditLogSerializer
from .tasks import confirm_transaction

logger = logging.getLogger("transactions")

# In-memory mock payment store
_mock_payments = {}


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        idempotency_key = request.headers.get("Idempotency-Key")

        # Check for duplicate
        if idempotency_key:
            existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                logger.info("Duplicate request detected", extra={
                    "transaction_id": existing.id, "idempotency_key": idempotency_key
                })
                serializer = self.get_serializer(existing)
                return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with db_transaction.atomic():
            tx = serializer.save(idempotency_key=idempotency_key)
            AuditLog.objects.create(
                transaction=tx,
                action="created",
                new_status="pending",
                details={"user_id": tx.user_id, "amount": str(tx.amount), "type": tx.type},
            )

        logger.info("Transaction created", extra={
            "transaction_id": tx.id, "user_id": tx.user_id,
            "amount": str(tx.amount), "type": tx.type,
        })

        # Schedule background confirmation
        confirm_transaction.delay(tx.id)

        return Response(
            TransactionSerializer(tx).data,
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
def paypal_create(request):
    tx_id = request.data.get("transaction_id")
    try:
        tx = Transaction.objects.get(id=tx_id)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)

    payment_id = f"PAY-{uuid.uuid4().hex[:16].upper()}"
    _mock_payments[payment_id] = {
        "transaction_id": tx.id,
        "amount": str(tx.amount),
        "status": "created",
    }

    tx.paypal_payment_id = payment_id
    tx.status = "processing"
    tx.save()

    AuditLog.objects.create(
        transaction=tx,
        action="paypal_payment_created",
        old_status="pending",
        new_status="processing",
        details={"payment_id": payment_id},
    )

    logger.info("PayPal payment created", extra={
        "transaction_id": tx.id, "payment_id": payment_id,
    })

    return Response({
        "payment_id": payment_id,
        "status": "created",
        "approval_url": f"https://mock-paypal.example.com/approve/{payment_id}",
    })


@api_view(["POST"])
def paypal_capture(request):
    payment_id = request.data.get("payment_id")
    payment = _mock_payments.get(payment_id)
    if not payment:
        return Response({"error": "Payment not found"}, status=404)

    payment["status"] = "captured"

    try:
        tx = Transaction.objects.get(paypal_payment_id=payment_id)
        tx.status = "completed"
        tx.save()
        AuditLog.objects.create(
            transaction=tx,
            action="paypal_payment_captured",
            old_status="processing",
            new_status="completed",
            details={"payment_id": payment_id},
        )
    except Transaction.DoesNotExist:
        pass

    logger.info("PayPal payment captured", extra={"payment_id": payment_id})
    return Response({"payment_id": payment_id, "status": "captured"})


@api_view(["POST"])
def paypal_webhook(request):
    event_type = request.data.get("event_type")
    payment_id = request.data.get("payment_id")
    webhook_status = request.data.get("status")

    logger.info("PayPal webhook received", extra={
        "event_type": event_type, "payment_id": payment_id, "status": webhook_status,
    })

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        try:
            tx = Transaction.objects.get(paypal_payment_id=payment_id)
            old_status = tx.status
            tx.status = "completed"
            tx.save()
            AuditLog.objects.create(
                transaction=tx,
                action="paypal_webhook_completed",
                old_status=old_status,
                new_status="completed",
                details={"payment_id": payment_id, "event_type": event_type},
            )
        except Transaction.DoesNotExist:
            pass

    return Response({"status": "ok"})
