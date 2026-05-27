import re
import unicodedata
import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

BASE = "https://www.aprovaconcursos.com.br"

SEARCHES = [
    ("professor",    "Professor"),
    ("pesquisador",  "Pesquisador"),
    ("epidemiolog",  "Epidemiologista"),
    ("nutricionista","Nutricionista"),
]


def _scrape_search(cargo_slug: str, cargo_label: str) -> list[dict]:
    url = f"{BASE}/concursos/?estado=SP&cargo={cargo_slug}"
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        cards = soup.select('a[href*="/concursos/"][class*="grid"]')
        for card in cards:
            href = card.get("href", "")
            if not href:
                continue
            full_url = BASE + href if href.startswith("/") else href
            text = card.get_text(" ", strip=True)

            # Extract organisation name from card text
            match = re.search(r"C[oó]digo\s+\d+\s+(.+)", text)
            org = match.group(1).strip() if match else text[-80:].strip()

            title = f"Concurso {cargo_label} — {org}"

            # Parse "City/STATE - Org" pattern
            loc_match = re.match(r"^([^/(]+)/([A-Z]{2})\b", org)
            if loc_match:
                city  = loc_match.group(1).strip()
                state = loc_match.group(2)
            else:
                city  = ""
                state = ""

            jobs.append({
                "id": f"concurso_{abs(hash(full_url))}",
                "title": title,
                "company": org,
                "location": f"{city}, {state}" if city else org[:60],
                "city": city,
                "state": state,
                "remote": False,
                "url": full_url,
                "source": "Aprovaconcursos",
                "type": "concurso",
            })
    except Exception as e:
        logger.warning(f"Aprovaconcursos error ({cargo_slug}): {e}")
    return jobs


def scrape() -> list[dict]:
    results = []
    seen_ids: set[str] = set()

    for slug, label in SEARCHES:
        for job in _scrape_search(slug, label):
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                results.append(job)

    logger.info(f"Concursos (aprovaconcursos): {len(results)} vagas coletadas")
    return results
