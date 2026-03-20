from django.shortcuts import render
from apps.ai.services import get_monthly_generations
from apps.ai.limits import PLAN_LIMITS
from apps.ai.models import Generation
import stripe
import json
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_ORDER = {
    "free": 0,
    "starter": 1,
    "creator": 2,
    "pro": 3,
}

def billing_portal(request):

    profile = request.user.userprofile

    session = stripe.billing_portal.Session.create(
        customer=profile.stripe_customer_id,

        return_url=request.build_absolute_uri("/subscription/")
    )

    return redirect(session.url)

@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

    except ValueError:
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Evento de pagamento concluído
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        customer_id = session["customer"]

        subscription_id = session["subscription"]

        plan = session["metadata"]["plan"]

        from apps.users.models import UserProfile

        profile = UserProfile.objects.get(
            stripe_customer_id=customer_id
        )

        profile.plan = plan
        profile.stripe_subscription_id = subscription_id
        profile.save()

    return HttpResponse(status=200)

def create_checkout_session(request, plan):

    profile = request.user.userprofile
    current_plan = profile.plan

    # bloqueia downgrade
    if PLAN_ORDER[plan] <= PLAN_ORDER[current_plan]:
        return redirect("subscription")

    price_id = settings.STRIPE_PRICES.get(plan)

    success_url = request.build_absolute_uri(
        reverse("payment_success", args=[plan])
    )

    cancel_url = request.build_absolute_uri(
        reverse("subscription")
    )

    session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        mode="subscription",

        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],

        customer_email=request.user.email,

        success_url=success_url,
        cancel_url=cancel_url,

    )

    return redirect(session.url)

def subscription(request):
  profile = request.user.userprofile
  plan = profile.plan

  limit = PLAN_LIMITS[plan]
  usage = get_monthly_generations(request.user)

  percentage = int((usage / limit) * 100)

  current_plan_level = PLAN_ORDER[plan]

  return render(request, "pages/subscription.html", {
    "plan": plan,
    "limit": limit,
    "usage": usage,
    "percentage": percentage,
    "current_plan_level": current_plan_level,
    "plan_order": PLAN_ORDER
  })

def payment_success(request, plan):

    profile = request.user.userprofile

    # temporário
    profile.plan = plan
    profile.save()

    return redirect("dashboard")

def change_plan(request, new_plan):

    profile = request.user.userprofile
    subscription_id = profile.stripe_subscription_id

    price_id = settings.STRIPE_PRICES[new_plan]

    subscription = stripe.Subscription.retrieve(subscription_id)

    current_price = subscription["items"]["data"][0]["price"]["id"]

    stripe.Subscription.modify(
        subscription_id,

        items=[{
            "id": subscription["items"]["data"][0].id,
            "price": price_id
        }],

        proration_behavior="none",

        billing_cycle_anchor="unchanged"
    )

    return redirect("subscription")


@login_required
def profile(request):
  return render(request, "pages/profile.html")