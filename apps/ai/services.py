from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from datetime import date
from .models import Generation
from apps.news.services import search_news, build_context
from apps.users.services import get_current_cycle

today = date.today().strftime('%d/%m/%Y')

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_monthly_generations(user):

    cycle_start, cycle_end = get_current_cycle(user.userprofile)

    return Generation.objects.filter(
        user=user,
        created_at__gte=cycle_start,
        created_at__lt=cycle_end
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

        articles = search_news(text)

        if not articles:
            context = "Nenhuma informação recente encontrada."
        else:
            context = build_context(articles)

        prompt = f"""
HOJE É {today}

Você é um social media profissional especializado em criação de conteúdo para redes sociais.

Sua tarefa é criar um post envolvente, claro e direto com base nas informações fornecidas.

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

- Linguagem natural e envolvente
- Direto ao ponto
- Tom humano (pode ser leve, informativo ou provocativo dependendo do tema)
- Frases curtas e fáceis de ler
- Evite repetições
- Use elementos que prendam atenção (ex: perguntas, chamadas, curiosidade)

---

FORMATO OBRIGATÓRIO (SEM EXCEÇÃO):

Linha 1: frase de impacto (hook)
Linha 2: contexto resumido (1 frase)
Linha 3 em diante: desenvolvimento com frases curtas e escaneáveis
Última linha: chamada para ação (CTA)

---

REGRAS IMPORTANTES:

- NÃO use ** ou qualquer markdown
- NÃO escreva "HOOK:", "CTA:" ou qualquer rótulo
- NÃO adicione explicações fora do post
- NÃO invente nomes, datas ou números
- Pode usar emojis com moderação (se fizer sentido)

"""

    elif content_type == "videoscript":

        articles = search_news(text)

        if not articles:
            context = "Nenhuma informação recente encontrada."
        else:
            context = build_context(articles)

        prompt = f"""
HOJE É {today}

Você é um roteirista profissional especializado em vídeos curtos para redes sociais.

Sua tarefa é criar um roteiro de vídeo envolvente, claro e direto com base nas informações fornecidas.

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

- Linguagem natural e dinâmica
- Direto ao ponto
- Tom envolvente e conversacional
- Frases curtas e fáceis de falar
- Evite repetições
- Priorize ritmo e retenção de atenção
- Seja persoasivo e provoque curiosidade

---

FORMATO OBRIGATÓRIO (SEM EXCEÇÃO):

Linha 1: gancho forte (primeiros 3 segundos)
Linha 2: contextualização rápida
Linha 3 em diante: desenvolvimento em sequência lógica (como se estivesse falando)
Última linha: chamada para ação (CTA)

---

REGRAS IMPORTANTES:

- NÃO use ** ou qualquer markdown
- NÃO escreva "GANCHO:", "CTA:" ou qualquer rótulo
- NÃO adicione explicações fora do roteiro
- NÃO invente nomes, datas ou números
- Pode usar pausas naturais (ex: "...") para dar ritmo
- Escreva como se fosse falado em voz alta

"""
    elif content_type == "headline":
        return

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