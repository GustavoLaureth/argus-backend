from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from django.db.models import Count
from datetime import timedelta
from apps.ai.services import get_monthly_generations
from apps.ai.limits import PLAN_LIMITS
from apps.ai.models import Generation
from django.utils import timezone
import json

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

@staff_member_required
def admin_dashboard(request):

  now = timezone.now()

  # 👥 usuários
  total_users = User.objects.count()

  new_users_7d = User.objects.filter(
    date_joined__gte=now - timedelta(days=7)
  ).count()

  # ⚡ atividade
  active_users_7d = Generation.objects.filter(
    created_at__gte=now - timedelta(days=7)
  ).values("user").distinct().count()

  # 📊 gerações
  total_generations = Generation.objects.count()

  generations_7d = Generation.objects.filter(
    created_at__gte=now - timedelta(days=7)
  ).count()

  # 💰 conversão (proxy)
  users_limit_reached = UserProfile.objects.filter(
    limit_reached=True
  ).count()

  # 🔥 tipos mais usados
  top_types = Generation.objects.values("content_type") \
    .annotate(total=Count("id")) \
    .order_by("-total")[:5]

  # 📈 uso por dia (últimos 7 dias)
  daily_usage = []
  for i in range(7):
    day = now - timedelta(days=i)
    count = Generation.objects.filter(
      created_at__date=day.date()
    ).count()

    daily_usage.append({
      "date": day.strftime("%d/%m"),
      "count": count
    })

  daily_usage.reverse()

  daily_label = [d["date"] for d in daily_usage]
  daily_values = [d["count"] for d in daily_usage]

  return render(request, "pages/admin_dashboard.html", {
      "total_users": total_users,
      "new_users_7d": new_users_7d,
      "active_users_7d": active_users_7d,
      "total_generations": total_generations,
      "generations_7d": generations_7d,
      "users_limit_reached": users_limit_reached,
      "top_types": top_types,
      "daily_labels": json.dumps(daily_label),
      "daily_values": json.dumps(daily_values),
  })