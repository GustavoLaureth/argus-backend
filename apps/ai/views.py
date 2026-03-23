from django.shortcuts import render
from .services import generate_content, get_monthly_generations, parse_news
from .models import Generation
from .limits import PLAN_LIMITS
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from urllib.parse import urlencode

@login_required
def create(request):

    result = None
    error = None

    title = None
    subtitle = None
    body = None

    if request.method == "POST":
        text = request.POST.get("text")
        content_type = request.POST.get("type")

        # pegar plano do usuário
        profile = request.user.userprofile

        limit = PLAN_LIMITS[profile.plan]

        usage = get_monthly_generations(request.user)

        # verificar limite
        if limit and usage >= limit:
            error = "Você atingiu o limite do seu plano."
        else:
            # gerar conteúdo com IA
            result = generate_content(text, content_type)

            if content_type == "news":
                title, subtitle, body = parse_news(result)

                if not title:

                    body = result.split("\n")

            # salvar no banco
            Generation.objects.create(
                user=request.user,
                input_text=text,
                output_text=result,
                content_type=content_type
            )

    return render(request, "pages/create.html", {
        "result": result,
        "error": error,
        "title": title,
        "subtitle": subtitle,
        "body": body,
        "error": error
    })

@login_required
def history(request):

    generations = Generation.objects.filter(
        user=request.user
    ).order_by("-created_at")

    query_params = request.GET.copy()

    if "page" in query_params:
        query_params.pop("page")

    search = request.GET.get("search", "").strip()
    if search:
        generations = generations.filter(
            Q(input_text__icontains=search) |
            Q(output_text__icontains=search)
        )
    
    types = request.GET.getlist("type")
    if types and "all" not in types:
        generations = generations.filter(content_type__in=types)

    # 📅 período
    period = request.GET.get("period")
    if period:
        now = timezone.now()

        if period == "7":
            generations = generations.filter(created_at__gte=now - timedelta(days=7))

        elif period == "30":
            generations = generations.filter(created_at__gte=now - timedelta(days=30))

        elif period == "90":
            generations = generations.filter(created_at__gte=now - timedelta(days=90))

    paginator = Paginator(generations, 10)
    page_number = request.GET.get('page')
    generations = paginator.get_page(page_number)

    for g in generations:
        if g.content_type == "news":
            title, subtitle, body = parse_news(g.output_text)

            g.title = title
            g.subtitle = subtitle
            g.body = body

    return render(request, "pages/history.html", {
        "generations": generations,
        "search": search,
        "selected_types": types,
        "selected_period": period,
        "query_params": urlencode(query_params)
    })