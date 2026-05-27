import re
import requests
import time
import logging
from config import GUPY_KEYWORDS

logger = logging.getLogger(__name__)

GUPY_API = "https://portal.api.gupy.io/api/v1/jobs"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; VagasBot/1.0)"}

# Additional searches targeting priority companies by name
PRIORITY_COMPANY_SEARCHES = [
    "einstein saude",
    "fiocruz",
    "impulso gov",
    "ieps saude",
    "pastoral crianca",
    "fundacao leman",
]


def _fetch_gupy_portal(keyword: str, limit: int = 20) -> list[dict]:
    jobs = []
    offset = 0
    while True:
        try:
            resp = requests.get(
                GUPY_API,
                params={"jobName": keyword, "limit": limit, "offset": offset},
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            batch = data.get("data", [])
            if not batch:
                break
            jobs.extend(batch)
            if len(batch) < limit:
                break
            offset += limit
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"Gupy portal error (keyword={keyword}): {e}")
            break
    return jobs


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "")[:800]


def _normalize(job: dict) -> dict:
    company = job.get("careerPageName", "") or job.get("company", {}).get("name", "")
    return {
        "id": f"gupy_{job.get('id', '')}",
        "title": job.get("name", ""),
        "company": company,
        "location": _build_location(job),
        "remote": job.get("isRemoteWork", False) or job.get("workplaceType", "") == "remote",
        "url": job.get("jobUrl", ""),
        "source": "Gupy",
        "type": "corporativa",
        "published_date": job.get("publishedDate", ""),
        "deadline": job.get("applicationDeadline") or "",
        "description": _strip_html(job.get("description", "")),
    }


def _build_location(job: dict) -> str:
    if job.get("isRemoteWork") or job.get("workplaceType", "") == "remote":
        return "Remoto"
    city = job.get("city", "") or ""
    state = job.get("state", "") or ""
    parts = [p for p in [city, state] if p]
    return ", ".join(parts) if parts else "Não informado"


def scrape() -> list[dict]:
    seen_ids: set[str] = set()
    results: list[dict] = []

    all_keywords = list(dict.fromkeys(GUPY_KEYWORDS + PRIORITY_COMPANY_SEARCHES))

    for kw in all_keywords:
        for raw in _fetch_gupy_portal(kw):
            norm = _normalize(raw)
            if norm["id"] not in seen_ids:
                seen_ids.add(norm["id"])
                results.append(norm)
        time.sleep(0.3)

    logger.info(f"Gupy: {len(results)} vagas coletadas")
    return results
