from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.ai.services import get_monthly_generations
from apps.ai.limits import PLAN_LIMITS
from apps.ai.models import Generation
from django.utils import timezone

@login_required
def dashboard(request):
  profile = request.user.userprofile
  plan = profile.plan
  limit = PLAN_LIMITS[plan]
  usage = get_monthly_generations(request.user)

  percentage = int((usage / limit) * 100)

  recent_generations = Generation.objects.filter(
    user=request.user
  ).order_by("-created_at")[:5]

  now = timezone.now()

  generations = Generation.objects.filter(
    user=request.user,
    created_at__year=now.year,
    created_at__month=now.month
  )

  generations_count = generations.count()

  # 🔥 2. tempo por tipo (regra de negócio)
  TIME_BY_TYPE = {
    "news": 10,
    "social": 5,
    "headline": 2,
  }

  total_minutes = 0

  for g in generations:
    total_minutes += TIME_BY_TYPE.get(g.content_type, 3)

  # 🔥 3. converter tempo
  hours = total_minutes // 60
  minutes = total_minutes % 60

  if hours > 0:
    time_saved = f"{hours}h {minutes}m"
  else:
    time_saved = f"{minutes} min"

  return render(request, "pages/dashboard.html", {
    "plan": plan,
    "limit": limit,
    "usage": usage,
    "percentage": percentage,
    "recent_generations": recent_generations,
    "time_saved": time_saved,
  })