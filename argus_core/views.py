from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.ai.services import get_monthly_generations
from apps.ai.limits import PLAN_LIMITS
from apps.ai.models import Generation

@login_required
def dashboard(request):
  profile = request.user.userprofile
  plan = profile.plan
  limit = PLAN_LIMITS[plan]
  usage = get_monthly_generations(request.user)

  recent_generations = Generation.objects.filter(
    user=request.user
  ).order_by("-created_at")[:5]

  return render(request, "pages/dashboard.html", {
    "plan": plan,
    "limit": limit,
    "usage": usage,
    "recent_generations": recent_generations
  })

@login_required
def profile(request):
  return render(request, "pages/profile.html")