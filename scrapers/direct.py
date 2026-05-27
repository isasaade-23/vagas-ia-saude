import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _generic_scrape(url: str, company: str, source_id_prefix: str) -> list[dict]:
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Try common job card selectors
        selectors = [
            "article", ".job", ".vaga", ".position", ".opening",
            "li.job-item", "div.job-card", ".career-item",
        ]
        cards = []
        for sel in selectors:
            cards = soup.select(sel)
            if cards:
                break

        # Last resort: all <a> tags with job-like text
        if not cards:
            cards = [
                a for a in soup.select("a[href]")
                if any(w in a.get_text().lower() for w in
                       ["vaga", "job", "posição", "analista", "pesquisa", "professor"])
            ]

        for card in cards:
            text = card.get_text(" ", strip=True)
            if len(text) < 10:
                continue
            link_el = card if card.name == "a" else card.select_one("a")
            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                base = url.split("/")[0] + "//" + url.split("/")[2]
                href = base + ("" if href.startswith("/") else "/") + href

            title_el = card.select_one("h2, h3, h4, strong, .title, .job-title")
            title = title_el.get_text(strip=True) if title_el else text[:100]

            jobs.append({
                "id": f"{source_id_prefix}_{abs(hash(href or title))}",
                "title": title,
                "company": company,
                "location": "Remoto",
                "remote": True,
                "url": href or url,
                "source": company,
                "type": "corporativa",
            })
    except Exception as e:
        logger.warning(f"Direct scrape error ({url}): {e}")
    return jobs


DIRECT_SOURCES = [
    {
        "url": "https://impulso.work/vagas",
        "company": "Impulso Gov",
        "prefix": "impulso",
    },
    {
        "url": "https://fundacaoleman.org.br/trabalhe-conosco/",
        "company": "Fundação Leman",
        "prefix": "leman",
    },
    {
        "url": "https://www.itausocial.org.br/trabalhe-conosco/",
        "company": "Itaú Social",
        "prefix": "itausocial",
    },
    {
        "url": "https://ieps.org.br/trabalhe-conosco/",
        "company": "IEPS",
        "prefix": "ieps",
    },
]


def scrape() -> list[dict]:
    results = []
    seen_ids: set[str] = set()

    for source in DIRECT_SOURCES:
        jobs = _generic_scrape(source["url"], source["company"], source["prefix"])
        for job in jobs:
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                results.append(job)

    logger.info(f"Direct pages: {len(results)} vagas coletadas")
    return results
