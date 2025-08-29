import re, json
from typing import List, Dict
from rapidfuzz import fuzz

def load_skill_list(path: str = "skills/skill_list.json") -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        skills = json.load(f)
    # normalize
    skills = [s.strip().lower() for s in skills if s.strip()]
    # de-duplicate while preserving order
    seen = set()
    unique = []
    for s in skills:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique

def _normalize_text(t: str) -> str:
    t = t.lower()
    # collapse whitespace
    t = re.sub(r"\s+", " ", t)
    return t

def _boundary_pattern(phrase: str) -> re.Pattern:
    # Use non-word boundaries to avoid matching substrings
    escaped = re.escape(phrase)
    return re.compile(rf"(?<!\w){escaped}(?!\w)")

def extract_candidate_skills(text: str, skill_list: List[str], fuzzy_threshold: int = 90) -> List[str]:
    """Return sorted list of skills found in `text` using exact boundary match + fuzzy partial match."""
    if not text:
        return []
    t = _normalize_text(text)
    found = set()

    # Exact boundary match pass
    for skill in skill_list:
        pat = _boundary_pattern(skill)
        if pat.search(t):
            found.add(skill)

    # Fuzzy pass for phrases (skip short 1-2 char tokens)
    for skill in skill_list:
        if skill in found or len(skill) < 3:
            continue
        score = fuzz.partial_ratio(skill, t)
        if score >= fuzzy_threshold:
            found.add(skill)

    return sorted(found)

def match_skills(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, List[str] | int]:
    rset = set(s.lower() for s in resume_skills)
    jset = set(s.lower() for s in jd_skills)
    matched = sorted(rset & jset)
    missing = sorted(jset - rset)
    extra = sorted(rset - jset)
    score = int(round((len(matched) / max(1, len(jset))) * 100))
    return {"matched": matched, "missing": missing, "extra": extra, "score": score}

def suggest_bullets(missing_skills: List[str]) -> List[str]:
    bullets = []
    for s in missing_skills:
        bullets.append(f"Implemented {s} in a project to solve X, improving Y by Z% (include metrics)." )
    return bullets

def build_report_md(score: int, matched: List[str], missing: List[str], extra: List[str], bullets: List[str], jd_excerpt: str) -> str:
    lines = []
    lines.append(f"# Resume Analysis Report\n")
    lines.append(f"**Score:** {score}%\n")
    lines.append("## Matched skills\n")
    lines.append("- " + ", ".join(matched) if matched else "- None")
    lines.append("\n## Missing skills\n")
    lines.extend([f"- {m}" for m in missing] or ["- None"])
    lines.append("\n## Extra (resume-only) skills\n")
    lines.append("- " + ", ".join(extra) if extra else "- None")
    if bullets:
        lines.append("\n## Suggested bullets\n")
        for b in bullets:
            lines.append(f"- {b}")
    if jd_excerpt:
        lines.append("\n## JD excerpt\n")
        lines.append("> " + jd_excerpt.replace("\n", " ") + "\n")
    return "\n".join(lines)
