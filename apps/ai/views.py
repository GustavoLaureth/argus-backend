from django.shortcuts import render
from .services import generate_content, get_monthly_generations
from .models import Generation
from .limits import PLAN_LIMITS
from django.contrib.auth.decorators import login_required

@login_required
def create(request):

    result = None
    error = None

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
            # salvar no banco
            Generation.objects.create(
                user=request.user,
                input_text=text,
                output_text=result,
                content_type=content_type
            )

    return render(request, "pages/create.html", {
        "result": result,
        "error": error
    })

@login_required
def history(request):

    generations = Generation.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "pages/history.html", {
        "generations": generations
    })