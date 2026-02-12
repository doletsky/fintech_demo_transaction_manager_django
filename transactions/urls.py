from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, paypal_create, paypal_capture, paypal_webhook

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("paypal/create/", paypal_create, name="paypal-create"),
    path("paypal/capture/", paypal_capture, name="paypal-capture"),
    path("paypal/webhook/", paypal_webhook, name="paypal-webhook"),
]
