import json
import os
from dotenv import load_dotenv
from google import genai
from knowledge import search_sources, verify_evidence

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

def classify_source(question: str):
    q = question.lower()
    if any(x in q for x in ["calendar", "semester start", "mid term", "dussehra", "diwali"]):
        return ["academic_calendar"]
    if "syllabus" in q or "unit" in q:
        return ["syllabus"]
    if any(x in q for x in ["class", "timetable", "period", "room", "lab", "tomorrow"]):
        return ["timetable", "faculty"]
    if any(x in q for x in ["teacher", "faculty", "who teaches"]):
        return ["faculty"]
    if "exam" in q:
        return ["examinations"]
    if "notice" in q:
        return ["notices"]
    if "event" in q:
        return ["events"]
    if "club" in q:
        return ["clubs"]
    if any(x in q for x in ["library", "facility", "lab"]):
        return ["facilities"]
    return ["all"]

def run_helpdesk(question, user, history):
    statuses = [
        "Understanding your request…",
        "Checking your profile/context…",
        "Planning the search…",
    ]

    selected = classify_source(question)
    statuses.append("Searching: " + ", ".join(selected))
    evidence = search_sources(question, user, selected)

    verification = verify_evidence(question, evidence, user)

    # Visible high-level replanning, without exposing chain-of-thought.
    if not verification["verified"] and selected != ["all"]:
        statuses.append("Replanning…")
        statuses.append("Checking another permitted source…")
        evidence = search_sources(question, user, ["all"])
        verification = verify_evidence(question, evidence, user)

    statuses.append("Checking evidence…")

    if not verification["verified"]:
        answer = "I couldn't verify this information from the available college sources."
        sources = [e["source"] for e in evidence]
        return {"answer": answer, "sources": sources, "statuses": statuses + ["Information insufficient."]}

    statuses.append("Verified.")
    answer = generate_answer(question, user, evidence)

    return {
        "answer": answer,
        "sources": [e["source"] for e in evidence],
        "statuses": statuses + ["Preparing answer…"],
    }

def generate_answer(question, user, evidence):
    if not evidence:
        return "I couldn't verify this information from the available college sources."

    context = "\n".join(
        f"SOURCE: {e['source']}\nSTATUS: {e.get('status','Verified')}\nDATA: {json.dumps(e['data'])}"
        for e in evidence
    )

    if not client:
        return "Gemini API key is not configured. Please add GEMINI_API_KEY to .env."

    prompt = f"""You are a college helpdesk assistant.
Answer ONLY from the supplied evidence.
Never invent college facts.
If the evidence does not answer the exact question, say:
"I couldn't verify this information from the available college sources."
Preserve the word Tentative whenever the source says Tentative.
User context: {json.dumps(user)}
Question: {question}
Evidence:
{context}
Give a short, clear answer suitable for a student/faculty/staff member."""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    return response.text.strip()
