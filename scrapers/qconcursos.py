import requests
import logging
from bs4 import BeautifulSoup
from config import CONCURSO_KEYWORDS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# QConcursos search URLs for health + SP
SEARCH_URLS = [
    "https://www.qconcursos.com/concursos-publicos/concursos?i[states][]=SP&i[categories][]=saude",
    "https://www.qconcursos.com/concursos-publicos/concursos?i[states][]=SP&i[categories][]=educacao",
]


def _matches_profile(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in CONCURSO_KEYWORDS)


def _scrape_qconcursos_page(url: str) -> list[dict]:
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        cards = soup.select("div.contest-card, article.contest-item, li.contest")
        if not cards:
            # fallback: search for links with contest data
            cards = soup.select("a[href*='/concursos-publicos/']")

        for card in cards:
            text = card.get_text(" ", strip=True)
            href = card.get("href", "") or (card.select_one("a") or {}).get("href", "")

            if not _matches_profile(text):
                continue

            title = ""
            title_el = card.select_one("h2, h3, .title, .name, strong")
            if title_el:
                title = title_el.get_text(strip=True)
            elif isinstance(card.get("href"), str):
                title = text[:120]
            if not title:
                title = text[:120]

            org_el = card.select_one(".organization, .org, .banca, .entity")
            company = org_el.get_text(strip=True) if org_el else "Concurso Público SP"

            url_full = href if href.startswith("http") else f"https://www.qconcursos.com{href}"

            jobs.append({
                "id": f"qconcursos_{abs(hash(url_full))}",
                "title": title,
                "company": company,
                "location": "São Paulo, SP",
                "remote": False,
                "url": url_full,
                "source": "QConcursos",
                "type": "concurso",
            })
    except Exception as e:
        logger.warning(f"QConcursos scrape error ({url}): {e}")
    return jobs


def _scrape_diario_oficial() -> list[dict]:
    """Fallback: Diário Oficial SP RSS for professor/researcher openings."""
    jobs = []
    rss_url = "https://www.imprensaoficial.com.br/rss/rss.aspx?portal=poder_executivo"
    try:
        resp = requests.get(rss_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        for item in soup.select("item")[:30]:
            title = item.find("title")
            link = item.find("link")
            desc = item.find("description")
            if not title:
                continue
            text = (title.get_text() + " " + (desc.get_text() if desc else "")).lower()
            if _matches_profile(text):
                jobs.append({
                    "id": f"doesp_{abs(hash(link.get_text() if link else title.get_text()))}",
                    "title": title.get_text(strip=True),
                    "company": "Diário Oficial SP",
                    "location": "São Paulo, SP",
                    "remote": False,
                    "url": link.get_text(strip=True) if link else "",
                    "source": "Diário Oficial SP",
                    "type": "concurso",
                })
    except Exception as e:
        logger.warning(f"Diário Oficial RSS error: {e}")
    return jobs


def scrape() -> list[dict]:
    results = []
    seen_ids: set[str] = set()

    for url in SEARCH_URLS:
        for job in _scrape_qconcursos_page(url):
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                results.append(job)

    for job in _scrape_diario_oficial():
        if job["id"] not in seen_ids:
            seen_ids.add(job["id"])
            results.append(job)

    logger.info(f"QConcursos/DOESP: {len(results)} vagas coletadas")
    return results
