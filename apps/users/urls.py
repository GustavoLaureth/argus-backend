from django.urls import path
from . import views

urlpatterns = [
    path("subscription/", views.subscription, name="subscription"),
    path("checkout/<str:plan>/", views.create_checkout_session, name="checkout"),
    path("stripe/webhook/", views.stripe_webhook),
    path("payment-success/<str:plan>", views.payment_success, name="payment_success"),
]