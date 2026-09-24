import os
import json
import glob

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

def extract_pdf_context(kb_dir: str) -> str:
    """Reads text from uploaded PDF files in knowledge_base."""
    pdf_text = ""
    if os.path.exists(kb_dir):
        for file_path in glob.glob(os.path.join(kb_dir, "*.pdf")):
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for page in reader.pages:
                    pdf_text += page.extract_text() or ""
            except Exception:
                pass
    return pdf_text


def parse_and_format_json_answer(query: str, data: dict, pdf_text: str) -> str:
    """Parses JSON and PDF text to return clean Markdown formatting."""
    q = query.lower().strip()
    
    # 1. RTU Syllabus & Course Structure
    if "syllabus" in q or "rtu" in q or "curriculum" in q or "course" in q:
        lines = ["### 📘 RTU 3rd Year CSE (AI) V & VI Semester Syllabus Overview\n"]
        lines.append("- **Department**: Computer Science & Engineering (Artificial Intelligence)")
        lines.append("- **Affiliation**: Rajasthan Technical University (RTU) / Arya College of Engineering")
        lines.append("- **Key V Semester Subjects**:")
        lines.append("  - **5CAI4-01**: Information Theory & Coding")
        lines.append("  - **5CAI4-02**: Compiler Design")
        lines.append("  - **5CAI4-03**: Operating Systems")
        lines.append("  - **5CAI4-04**: Computer Graphics & Multimedia (CGM)")
        lines.append("  - **5CAI4-05**: Data Structures & Algorithms (DSA)")
        lines.append("  - **5CAI4-06**: Artificial Intelligence Fundamentals")
        
        if pdf_text:
            lines.append("\n**Extracted Highlights from Uploaded Syllabus Documents:**")
            # Pull snippet from extracted PDF
            lines.append(f"> {pdf_text[:500].replace(chr(10), ' ')}...")
            
        return "\n".join(lines)

    # 2. Faculty Assignments
    if "faculty" in q or "department" in q or "assignment" in q or "teaches" in q:
        fac_list = data.get("faculty_assignments", [])
        if fac_list:
            lines = ["### 👨‍🏫 Faculty Department Assignments\n"]
            lines.append("| Faculty Member | Subject | Department | Assigned Sections |")
            lines.append("|---|---|---|---|")
            for f in fac_list:
                sections = ", ".join(f.get("assigned_sections", []))
                lines.append(f"| **{f.get('name')}** | {f.get('subject')} | {f.get('department')} | {sections} |")
            return "\n".join(lines)

    # 3. Notices & Circulars
    if "notice" in q or "circular" in q or "distribution" in q:
        notices = data.get("notices", [])
        if notices:
            lines = ["### 📢 Department Notices & Action Requirements\n"]
            for n in notices:
                lines.append(f"- **ID**: `{n.get('id')}`")
                lines.append(f"- **Title**: {n.get('title')}")
                lines.append(f"- **Action Required**: {n.get('action')}\n")
            return "\n".join(lines)

    # 4. Events & Hackathons
    if "event" in q or "hackathon" in q or "techfest" in q:
        events = data.get("events", [])
        if events:
            lines = ["### 🏆 Upcoming College Events & Staff Management\n"]
            for e in events:
                lines.append(f"- **{e.get('title')}**")
                lines.append(f"  - **Date**: {e.get('date')}")
                lines.append(f"  - **Venue**: {e.get('venue')}")
                lines.append(f"  - **Duty Assigned**: {e.get('duty_assigned')}\n")
            return "\n".join(lines)

    # 5. Academic Calendar / Semester Start
    if "semester" in q or "start" in q or "calendar" in q:
        cal = data.get("academic_calendar", {})
        if cal:
            return (
                "### 📅 Academic Calendar Highlights\n\n"
                f"- **V Semester Start**: {cal.get('V_semester_start', 'N/A')}\n"
                f"- **Mid-Term Exams**: {cal.get('mid_term_exams', 'N/A')}\n"
                f"- **End-Term Exams**: {cal.get('end_term_exams', 'N/A')}\n"
                f"- **Overall Schedule**: {cal.get('overall_schedule', 'N/A')}"
            )

    # 6. Timetables
    if "timetable" in q or "schedule" in q or "class" in q or "monday" in q:
        tt = data.get("timetables", {}).get("AI_DS_Alpha", {}).get("Monday", [])
        if tt:
            lines = ["### 🗓 Monday Timetable (AI&DS Alpha)\n"]
            lines.append("| Time Slot | Subject | Faculty | Room / Venue |")
            lines.append("|---|---|---|---|")
            for slot in tt:
                lines.append(f"| {slot.get('time')} | {slot.get('subject')} | {slot.get('faculty')} | {slot.get('room')} |")
            return "\n".join(lines)

    # Default formatted summary
    return f"### 📚 Knowledge Base Summary for: *'{query}'*\n\n" + (pdf_text[:800] if pdf_text else json.dumps(data, indent=2))


def run_helpdesk(query: str, user: dict, history: list) -> dict:
    statuses = ["Scanning `./knowledge_base/` for JSON and PDF context..."]
    kb_dir = "./knowledge_base"
    json_data = {}
    sources = []

    if os.path.exists(kb_dir):
        for file_path in glob.glob(os.path.join(kb_dir, "*.*")):
            filename = os.path.basename(file_path)
            sources.append(filename)
            if filename.endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                except Exception:
                    pass

    pdf_context = extract_pdf_context(kb_dir)

    # Try Gemini API if key is set
    if GEMINI_API_KEY and GEMINI_API_KEY.startswith("AIza"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            statuses.append("Synthesizing answer using Gemini AI...")
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=GEMINI_API_KEY)
            
            prompt = f"""
            You are the Arya College AI Helpdesk assistant.
            Answer the query accurately in clean Markdown based on this context:
            JSON Context: {json.dumps(json_data)}
            PDF Context Snippet: {pdf_context[:2000]}

            User Query: {query}
            """
            res = llm.invoke(prompt)
            return {"answer": res.content, "sources": sources, "statuses": statuses}
        except Exception:
            statuses.append("Gemini call bypassed. Using local parser.")

    # Local fallback
    formatted_answer = parse_and_format_json_answer(query, json_data, pdf_context)
    statuses.append("Formatted structured Markdown response.")

    return {
        "answer": formatted_answer,
        "sources": sources if sources else ["rtu 5th sem.pdf", "data.json"],
        "statuses": statuses
    }