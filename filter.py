from datetime import datetime, timezone, timedelta

from config import (
    HEALTH_KEYWORDS, DATA_KEYWORDS, ROLE_KEYWORDS, ALL_KEYWORDS,
    PRIORITY_COMPANIES, SCORE_THRESHOLD, PRIORITY_SCORE_BOOST, MAX_JOB_AGE_DAYS,
)


def _is_too_old(job: dict) -> bool:
    """
    Rejeita vagas cujo prazo de inscrição (deadline) já passou.
    Se não há deadline, usa published_date com janela de MAX_JOB_AGE_DAYS.
    Concursos sem data são mantidos.
    """
    deadline = job.get("deadline") or ""
    if deadline:
        try:
            dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            # Keep if deadline is in the future (or within last 3 days grace)
            return dt < datetime.now(timezone.utc) - timedelta(days=3)
        except Exception:
            pass

    pub = job.get("published_date") or ""
    if pub:
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_JOB_AGE_DAYS)
            return dt < cutoff
        except Exception:
            pass

    return False  # sem data alguma → mantém


def _is_wrong_location(job: dict) -> bool:
    """Rejeita vagas presenciais fora de SP/Brasil."""
    if job.get("remote"):
        return False  # remoto: aceito em qualquer lugar
    loc = (job.get("location") or "").lower()
    # Concursos já vêm com "São Paulo, SP" — OK
    if "são paulo" in loc or "sao paulo" in loc or "sp" in loc:
        return False
    if not loc or loc == "não informado":
        return False  # sem info de local → mantém
    return True  # presencial em outro estado → rejeita


def _score(job: dict) -> tuple[int, bool]:
    title   = (job.get("title", "") or "").lower()
    company = (job.get("company", "") or "").lower()
    desc    = (job.get("description", "") or "").lower()
    url     = (job.get("url", "") or "").lower()

    # Full text for keyword scoring
    full_text = f"{title} {company} {desc}"

    # Check priority company first
    is_priority = False
    for key in PRIORITY_COMPANIES:
        if key in company or key in url:
            is_priority = True
            break

    # Health keyword must appear somewhere (title, company, or description)
    has_health = any(kw in full_text for kw in HEALTH_KEYWORDS)
    has_role   = any(kw in full_text for kw in ROLE_KEYWORDS)
    is_concurso = job.get("type") == "concurso"

    # Concurso jobs with professor/pesquisador already came from health-filtered search
    if is_concurso and has_role:
        pass  # allow
    elif not has_health and not is_priority:
        return 0, False  # no health context → disqualified

    score = sum(1 for kw in ALL_KEYWORDS if kw in full_text)
    if is_priority:
        score += PRIORITY_SCORE_BOOST

    return score, is_priority


def rank_and_filter(jobs: list[dict]) -> list[dict]:
    scored = []
    for job in jobs:
        if _is_too_old(job):
            continue
        if _is_wrong_location(job):
            continue
        score, is_priority = _score(job)
        if score >= SCORE_THRESHOLD:
            scored.append({**job, "score": score, "priority": is_priority})

    scored.sort(key=lambda j: (j["priority"], j["score"]), reverse=True)
    return scored
