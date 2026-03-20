from django.urls import path
from . import views

urlpatterns = [
    path("subscription/", views.subscription, name="subscription"),
    path("profile/", views.profile, name="profile"),
    path("checkout/<str:plan>/", views.create_checkout_session, name="checkout"),
    path("stripe/webhook/", views.stripe_webhook),
    path("payment-success/<str:plan>", views.payment_success, name="payment_success"),
    path("billing-portal/", views.billing_portal, name="billing_portal")
]