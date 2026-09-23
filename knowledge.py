import json
from pathlib import Path


KB_PATH = Path(__file__).parent / "data" / "knowledge.json"


def load_knowledge():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def search_sources(question, user, selected=None):
    records = load_knowledge()

    question_lower = question.lower()
    words = [w for w in question_lower.split() if len(w) > 2]

    results = []

    for item in records:
        category = item.get("category", "unknown")

        # Respect selected source/category
        if selected and selected != "all":
            if isinstance(selected, list):
                if category not in selected:
                    continue
            elif category != selected:
                continue

        # User-context filtering
        user_department = str(user.get("department", "")).lower()
        user_semester = str(user.get("semester", "")).lower()
        user_section = str(user.get("section", "")).lower()

        item_department = str(item.get("department", "all")).lower()
        item_semester = str(item.get("semester", "all")).lower()
        item_section = str(item.get("section", "all")).lower()

        if item_department not in ("all", "", user_department):
            continue

        if item_semester not in ("all", "", user_semester):
            continue

        if item_section not in ("all", "", user_section):
            continue

        # Search BOTH top-level fields and nested data
        searchable = json.dumps(item, ensure_ascii=False).lower()

        score = 0

        for word in words:
            if word in searchable:
                score += 1

        # Category relevance
        if category in question_lower:
            score += 3

        # Special keywords
        if "calendar" in question_lower and category == "academic_calendar":
            score += 5

        if any(x in question_lower for x in ["event", "events", "program", "hackathon"]):
            if category == "events":
                score += 5

        if any(x in question_lower for x in ["timetable", "schedule", "class"]):
            if category == "timetable":
                score += 5

        if any(x in question_lower for x in ["teacher", "faculty", "professor", "who teaches"]):
            if category == "faculty":
                score += 5

        if any(x in question_lower for x in ["exam", "examination", "test"]):
            if category == "examinations":
                score += 5

        if score > 0:
            results.append((score, item))

    # Highest relevance first
    results.sort(key=lambda x: x[0], reverse=True)

    return [item for score, item in results[:10]]


def verify_evidence(question, evidence, user):
    if not evidence:
        return {
            "verified": False,
            "reason": "No matching college evidence was found."
        }

    for item in evidence:
        department = str(item.get("department", "all")).lower()
        user_department = str(user.get("department", "")).lower()

        if department not in ("all", "", user_department):
            continue

        semester = str(item.get("semester", "all")).lower()
        user_semester = str(user.get("semester", "")).lower()

        if semester not in ("all", "", user_semester):
            continue

        status = str(item.get("status", "Verified")).lower()

        if status != "unavailable":
            return {
                "verified": True,
                "reason": "Evidence matches the user's context."
            }

    return {
        "verified": False,
        "reason": "The available evidence does not match the user's context."
    }