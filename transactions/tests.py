from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Transaction, AuditLog


@override_settings(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    CELERY_TASK_ALWAYS_EAGER=True,
)
class TransactionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_transaction(self):
        resp = self.client.post("/api/transactions/", {
            "user_id": 1, "amount": "100.00", "type": "deposit",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["amount"], "100.00")
        self.assertEqual(resp.data["status"], "pending")

    def test_list_transactions(self):
        Transaction.objects.create(user_id=1, amount=50, type="deposit")
        resp = self.client.get("/api/transactions/")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_idempotency(self):
        data = {"user_id": 1, "amount": "200.00", "type": "payment"}
        resp1 = self.client.post(
            "/api/transactions/", data, format="json",
            HTTP_IDEMPOTENCY_KEY="key-123",
        )
        resp2 = self.client.post(
            "/api/transactions/", data, format="json",
            HTTP_IDEMPOTENCY_KEY="key-123",
        )
        self.assertEqual(resp1.data["id"], resp2.data["id"])
        self.assertEqual(Transaction.objects.filter(idempotency_key="key-123").count(), 1)

    def test_audit_log_created(self):
        self.client.post("/api/transactions/", {
            "user_id": 1, "amount": "50.00", "type": "withdrawal",
        }, format="json")
        self.assertEqual(AuditLog.objects.filter(action="created").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="created").first().action, "created")

    def test_paypal_create(self):
        tx = Transaction.objects.create(user_id=1, amount=100, type="payment")
        resp = self.client.post("/api/paypal/create/", {"transaction_id": tx.id}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "created")
        self.assertIn("payment_id", resp.data)

    def test_paypal_create_not_found(self):
        resp = self.client.post("/api/paypal/create/", {"transaction_id": 99999}, format="json")
        self.assertEqual(resp.status_code, 404)

    def test_paypal_webhook(self):
        tx = Transaction.objects.create(user_id=1, amount=100, type="payment", paypal_payment_id="PAY-TEST123")
        resp = self.client.post("/api/paypal/webhook/", {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "payment_id": "PAY-TEST123",
            "status": "completed",
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        tx.refresh_from_db()
        self.assertEqual(tx.status, "completed")
