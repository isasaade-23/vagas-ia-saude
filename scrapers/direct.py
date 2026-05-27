import json
import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

# Priority companies with Gupy subdomains
GUPY_COMPANY_SLUGS = [
    ("itausocial",    "Itaú Social"),
    ("leman",         "Fundação Leman"),
    ("impulsogovbr",  "Impulso Gov"),
    ("einstein",      "Einstein"),
    ("ieps",          "IEPS"),
]


def _fetch_gupy_company_jobs(slug: str, company_name: str) -> list[dict]:
    url = f"https://{slug}.gupy.io/jobs"
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        tag = soup.find("script", id="__NEXT_DATA__")
        if not tag:
            logger.warning(f"No __NEXT_DATA__ on {url}")
            return []
        data = json.loads(tag.string)
        raw_jobs = data.get("props", {}).get("pageProps", {}).get("jobs", [])
        for j in raw_jobs:
            wp = j.get("workplace", {})
            addr = wp.get("address", {})
            workplace_type = wp.get("workplaceType", "")
            is_remote = workplace_type == "remote"
            city = addr.get("city", "")
            state = addr.get("stateShortName", "")
            location = "Remoto" if is_remote else ", ".join(p for p in [city, state] if p) or "Não informado"
            job_id = j.get("id", "")
            jobs.append({
                "id": f"gupy_direct_{slug}_{job_id}",
                "title": j.get("title", ""),
                "company": company_name,
                "location": location,
                "remote": is_remote,
                "url": f"https://{slug}.gupy.io/jobs/{job_id}",
                "source": f"Gupy ({company_name})",
                "type": "corporativa",
            })
    except Exception as e:
        logger.warning(f"Direct Gupy scrape error ({slug}): {e}")
    return jobs


def scrape() -> list[dict]:
    results = []
    seen_ids: set[str] = set()

    for slug, name in GUPY_COMPANY_SLUGS:
        for job in _fetch_gupy_company_jobs(slug, name):
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                results.append(job)

    logger.info(f"Direct (priority companies): {len(results)} vagas coletadas")
    return results
