from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from datetime import date
from .models import Generation
from apps.news.services import search_news, build_context

today = date.today().strftime('%d/%m/%Y')

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_monthly_generations(user):

    now = timezone.now()

    return Generation.objects.filter(
        user=user,
        created_at__year=now.year,
        created_at__month=now.month
    ).count()

def generate_content(text, content_type):

    if content_type == "news":

        articles = search_news(text)

        if not articles:
            context = "Nenhuma informação recente encontrada."
        else:
            context = build_context(articles)

        prompt = f"""
HOJE É {today}

Você é um jornalista profissional especializado em notícias.

Sua tarefa é escrever uma notícia clara, precisa e confiável com base nas informações fornecidas.

---

CONTEXTO:
{context}

---

TEMA:
{text}

---

INSTRUÇÕES:

- Baseie-se APENAS no CONTEXTO fornecido
- Se não houver informações suficientes, utilize o TEMA como base e deixe claro que são informações gerais
- NÃO invente fatos
- NÃO use conhecimento externo

---

ESTILO:

- Linguagem jornalística real e natural
- Direto e objetivo
- Evite frases genéricas ou vagas
- Evite repetições
- Use detalhes concretos sempre que possível
- Corrija erros gramaticais antes de finalizar

---

FORMATO OBRIGATÓRIO (SEM EXCEÇÃO):

Linha 1: título da notícia  
Linha 2: subtítulo (1 frase resumindo o fato)  
Linha 3 em diante: corpo da notícia com parágrafos curtos  

---

REGRAS IMPORTANTES:

- NÃO use ** ou qualquer markdown
- NÃO escreva "TÍTULO:", "SUBTÍTULO:" ou "CORPO:"
- NÃO adicione explicações fora da notícia
- NÃO invente nomes, datas ou números

---

Agora escreva a notícia.

"""

    elif content_type == "social":

        prompt = f"""
Transforme o texto abaixo em um post para redes sociais:

{text}
"""

    elif content_type == "headline":

        prompt = f"""
Crie um título chamativo para o texto abaixo:

{text}
"""

    else:
        return "Tipo de conteúdo inválido"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    print(prompt)

    return response.choices[0].message.content

def parse_news(content):

    lines = [line.strip() for line in content.split("\n") if line.strip()]

    title = lines[0] if len(lines) > 0 else ""
    subtitle = lines[1] if len(lines) > 1 else ""
    body = lines[2:] if len(lines) > 2 else []

    return title, subtitle, body