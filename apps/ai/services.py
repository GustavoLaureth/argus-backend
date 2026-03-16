from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from .models import Generation

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_monthly_generations(user):

    now = timezone.now()

    return Generation.objects.filter(
        user=user,
        created_at__year=now.year,
        created_at__month=now.month
    ).count()

def generate_content(text, content_type):

    prompts = {
        "news": f"Transforme o texto abaixo em uma notícia jornalística:\n\n{text}",
        "social": f"Transforme o texto abaixo em um post para redes sociais:\n\n{text}",
        "headline": f"Crie um título chamativo para o texto:\n\n{text}",
    }

    prompt = prompts.get(content_type)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content