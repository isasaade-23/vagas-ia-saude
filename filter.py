from config import (
    ALL_KEYWORDS, PRIORITY_COMPANIES,
    SCORE_THRESHOLD, PRIORITY_SCORE_BOOST,
)


def _score(job: dict) -> tuple[int, bool]:
    searchable = f"{job.get('title', '')} {job.get('company', '')}".lower()

    score = sum(1 for kw in ALL_KEYWORDS if kw in searchable)

    is_priority = False
    company_lower = job.get("company", "").lower()
    url_lower = job.get("url", "").lower()
    for key, _ in PRIORITY_COMPANIES.items():
        # Match against company name or URL, but not generic title text
        if key in company_lower or key in url_lower:
            score += PRIORITY_SCORE_BOOST
            is_priority = True
            break

    return score, is_priority


def rank_and_filter(jobs: list[dict]) -> list[dict]:
    scored = []
    for job in jobs:
        score, is_priority = _score(job)
        if score >= SCORE_THRESHOLD:
            scored.append({**job, "score": score, "priority": is_priority})

    scored.sort(key=lambda j: (j["priority"], j["score"]), reverse=True)
    return scored
