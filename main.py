import json
import logging
import os
from pathlib import Path

from scrapers import gupy, qconcursos, direct
from filter import rank_and_filter
from notifier import send, send_summary
from config import MAX_JOBS_PER_RUN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")

SEEN_FILE = Path(__file__).parent / "data" / "seen_jobs.json"


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_seen(seen: set[str]) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    logger.info("Iniciando scraping de vagas...")

    # Collect from all sources
    all_jobs: list[dict] = []
    for scraper_mod in (gupy, qconcursos, direct):
        try:
            all_jobs.extend(scraper_mod.scrape())
        except Exception as e:
            logger.error(f"Erro no scraper {scraper_mod.__name__}: {e}")

    logger.info(f"Total bruto: {len(all_jobs)} vagas")

    # Filter & rank
    ranked = rank_and_filter(all_jobs)
    logger.info(f"Após filtro de relevância: {len(ranked)} vagas")

    # Deduplicate against seen
    seen = load_seen()
    new_jobs = [j for j in ranked if j["id"] not in seen]
    already_seen = len(ranked) - len(new_jobs)

    logger.info(f"Novas (não enviadas antes): {len(new_jobs)}")

    # Cap and send
    to_send = new_jobs[:MAX_JOBS_PER_RUN]
    send(to_send)
    send_summary(len(new_jobs), already_seen)

    # Persist seen IDs (all ranked, not just to_send)
    for j in ranked:
        seen.add(j["id"])
    save_seen(seen)

    logger.info("Concluído.")


if __name__ == "__main__":
    main()
