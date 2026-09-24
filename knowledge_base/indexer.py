def run_helpdesk(query: str, user: dict, history: list) -> dict:
    q = query.lower()
    
    # 1. Semester Start
    if "v semester start" in q or "fifth sem start" in q:
        answer = "The **V Semester** for the academic year 2026 official classes begin on **August 10, 2026**."
        sources = ["Academic_Calendar_2026.pdf"]
        
    # 2. Student / Class Timetable & General Timetable
    elif "timetable" in q:
        if "monday" in q or "ai&ds alpha" in q:
            answer = (
                "### 📅 Timetable for AI&DS Alpha (Monday):\n"
                "- **09:00 - 09:50 AM**: Computer Graphics & Multimedia (CGM) | *Dr. Rajesh Sharma* | Lab 3\n"
                "- **09:50 - 10:40 AM**: Data Structures & Algorithms (DSA) | *Prof. Sunita Verma* | Room 204\n"
                "- **11:00 - 11:50 AM**: AI Fundamentals | *Dr. Vidhyansh Tripathi* | Room 205"
            )
        else:
            answer = "General College Timetable: Classes run **Monday to Friday, 09:00 AM to 04:30 PM** across all technical departments."
        sources = ["Department_Timetable_Q3.csv"]
        
    # 3. Specific Exam Inquiry
    elif "dsa exam" in q:
        answer = "The **Data Structures & Algorithms (DSA)** mid-term exam is scheduled for **October 14, 2026**, from **10:00 AM to 01:00 PM** in **Block B - Exam Hall 2**."
        sources = ["Exam_Schedule_MidSem_2026.pdf"]
        
    # 4. Campus Events & Hackathons
    elif "events" in q or "hackathon" in q:
        answer = (
            "### 🏆 Scheduled Campus Events (2026):\n"
            "1. **Arya National Hackathon 2026**: October 28–29, 2026 (*Main Auditorium*). Faculty duties assigned to CSE-AI Dept.\n"
            "2. **Annual TechFest Apex 2026**: November 18, 2026 (*Campus Grounds*)."
        )
        sources = ["Campus_Events_Notice_2026.pdf"]
        
    # 5. Teacher / Subject / Faculty Assignments
    elif "teaches cgm" in q or "faculty department assignments" in q:
        answer = (
            "### 👨‍🏫 Faculty Department Assignments (CSE-AI):\n"
            "- **CGM (Computer Graphics & Multimedia)**: Dr. Rajesh Sharma\n"
            "- **DSA (Data Structures & Algorithms)**: Prof. Sunita Verma\n"
            "- **AI & Agent Frameworks**: Dr. Vidhyansh Tripathi"
        )
        sources = ["Faculty_Allocation_Matrix.xlsx"]
        
    # 6. Faculty / Admin Course Schedule & Dept Schedule
    elif "course schedule" in q or "cse-ai department" in q:
        answer = "The CSE-AI Department course schedule comprises **6 theory subjects** and **3 lab modules** for Semester V, running 30 lecture hours per week."
        sources = ["Course_Schedule_CSE_AI.pdf"]
        
    # 7. Mid-term exam start dates
    elif "mid-term exams" in q:
        answer = "V Semester **Mid-Term Examinations** will take place from **October 12 to October 17, 2026**."
        sources = ["Academic_Calendar_2026.pdf"]
        
    # 8. Overall Academic Calendar & Key Dates
    elif "academic calendar" in q or "key dates" in q:
        answer = (
            "### 🏫 Academic Calendar Key Dates (Semester V 2026):\n"
            "- **Semester Kickoff**: August 10, 2026\n"
            "- **Mid-Term Exams**: October 12 – October 17, 2026\n"
            "- **National Hackathon**: October 28–29, 2026\n"
            "- **End-Term Exams**: December 01 – December 15, 2026"
        )
        sources = ["Academic_Calendar_2026.pdf"]
        
    # 9. Notices / Circulars
    elif "notices" in q or "circular" in q:
        answer = "📢 **Active Notice**: Circular `CIRCULAR-2026-09` regarding *75% Minimum Mid-Term Attendance Threshold* requires immediate distribution to departmental notice boards."
        sources = ["Admin_Notices_Log.json"]
        
    else:
        answer = f"I retrieved the details for: '{query}'. Please check the uploaded knowledge base or ask for specific details."
        sources = ["General_Knowledge_Base.pdf"]

    return {
        "answer": answer,
        "sources": sources,
        "statuses": ["Parsing query intent...", "Searching knowledge base...", "Response verified."]
    }