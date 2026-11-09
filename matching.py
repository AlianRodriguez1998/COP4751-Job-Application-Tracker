"""Transparent job-to-skill comparison, independent of Flask and MySQL."""
import json


def skills_from_text(text):
    """Return distinct, trimmed skills in entered order, matching case-insensitively."""
    result = []
    seen = set()
    for part in (text or '').split(','):
        value = part.strip()
        if value and value.casefold() not in seen:
            seen.add(value.casefold())
            result.append(value)
    return result


def requirement_skills(value):
    """Requirements JSON is a list, or an object with a `skills` list."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return []
    if isinstance(value, dict):
        value = value.get('skills', [])
    if not isinstance(value, list):
        return []
    return skills_from_text(','.join(x for x in value if isinstance(x, str)))


def rank_jobs(jobs, own_skills):
    owned = {s.casefold() for s in own_skills}
    ranked = []
    for job in jobs:
        required = requirement_skills(job.get('requirements'))
        matched = [s for s in required if s.casefold() in owned]
        missing = [s for s in required if s.casefold() not in owned]
        # A job with no listed requirements cannot be evaluated; mark it as such.
        percentage = round(100 * len(matched) / len(required)) if required else None
        ranked.append({**job, 'required_skills': required, 'matched_skills': matched,
                       'missing_skills': missing, 'matched_count': len(matched),
                       'required_count': len(required), 'percentage': percentage})
    return sorted(ranked, key=lambda j: (j['percentage'] is None, -(j['percentage'] or 0),
                                         str(j.get('job_title', '')).casefold()))
