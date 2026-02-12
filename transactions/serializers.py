from rest_framework import serializers
from .models import Transaction, AuditLog


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id", "user_id", "amount", "type", "status",
            "idempotency_key", "paypal_payment_id",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "paypal_payment_id", "created_at", "updated_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "transaction", "action", "old_status", "new_status", "details", "created_at"]
