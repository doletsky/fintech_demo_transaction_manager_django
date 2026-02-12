from django.contrib import admin
from .models import Transaction, AuditLog

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "user_id", "amount", "type", "status", "created_at"]
    list_filter = ["type", "status"]

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction", "action", "old_status", "new_status", "created_at"]
