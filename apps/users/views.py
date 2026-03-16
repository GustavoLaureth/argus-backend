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

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_ORDER = {
    "free": 0,
    "starter": 1,
    "creator": 2,
    "pro": 3,
}

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

        customer_email = session["customer_email"]

        plan = session["metadata"]["plan"]

        from django.contrib.auth.models import User

        user = User.objects.get(email=customer_email)

        profile = user.userprofile
        profile.plan = plan
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