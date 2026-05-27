import os
import requests
import logging

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

COLOR_PRIORITY = 0xFF6B00   # laranja — empresa prioritária
COLOR_CONCURSO = 0x9B59B6   # roxo — concurso público
COLOR_NORMAL = 0x0099FF     # azul — vaga corporativa normal


def _build_embed(job: dict) -> dict:
    title = job["title"]
    company = job["company"]
    location = job.get("location", "Não informado")
    url = job.get("url", "")
    source = job.get("source", "")
    is_priority = job.get("priority", False)
    job_type = job.get("type", "corporativa")
    score = job.get("score", 0)

    if is_priority:
        color = COLOR_PRIORITY
        prefix = "⭐ PRIORITÁRIA"
    elif job_type == "concurso":
        color = COLOR_CONCURSO
        prefix = "📋 CONCURSO"
    else:
        color = COLOR_NORMAL
        prefix = "💼 Vaga"

    remote_tag = " 🌐 Remoto" if job.get("remote") else ""
    fields = [
        {"name": "Empresa", "value": company, "inline": True},
        {"name": "Local", "value": f"{location}{remote_tag}", "inline": True},
        {"name": "Fonte", "value": source, "inline": True},
    ]

    embed = {
        "title": f"{prefix}: {title[:200]}",
        "color": color,
        "fields": fields,
        "footer": {"text": f"Score de relevância: {score}"},
    }
    if url:
        embed["url"] = url

    return embed


def _chunk(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def send(jobs: list[dict]) -> None:
    if not WEBHOOK_URL:
        logger.error("DISCORD_WEBHOOK_URL não configurada")
        return
    if not jobs:
        logger.info("Nenhuma vaga nova para enviar")
        return

    embeds = [_build_embed(j) for j in jobs]

    # Discord allows max 10 embeds per message
    for batch in _chunk(embeds, 10):
        payload = {
            "username": "VagasBot IA Saúde",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2037/2037565.png",
            "embeds": batch,
        }
        try:
            resp = requests.post(WEBHOOK_URL, json=payload, timeout=15)
            resp.raise_for_status()
            logger.info(f"Enviados {len(batch)} embeds ao Discord")
        except Exception as e:
            logger.error(f"Erro ao enviar ao Discord: {e}")


def send_summary(total_new: int, total_seen: int) -> None:
    if not WEBHOOK_URL or total_new == 0:
        return
    payload = {
        "username": "VagasBot IA Saúde",
        "embeds": [{
            "title": "Resumo do scraping",
            "description": (
                f"**{total_new}** vagas novas encontradas\n"
                f"**{total_seen}** vagas já conhecidas (ignoradas)"
            ),
            "color": 0x2ECC71,
            "footer": {"text": "Próxima busca em ~6h"},
        }],
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=15)
    except Exception as e:
        logger.warning(f"Erro ao enviar resumo: {e}")
