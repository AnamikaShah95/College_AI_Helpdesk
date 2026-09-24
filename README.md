<div align="center">

# 🎓 Arya College of Engineering — AI Helpdesk Agent
### *Autonomous Multi-Role Helpdesk & RAG Knowledge Engine*

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![LLM Model](https://img.shields.io/badge/AI-Google%20Gemini%20Flash-4285F4?style=for-the-badge&logo=googlegemini)
![RAG Vector Database](https://img.shields.io/badge/VectorDB-ChromaDB-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<br/>

An intelligent, context-aware AI College Helpdesk built for **Students, Faculty, and Staff/Admin**. It dynamically processes structured college data (`data.json`) and unstructured RTU syllabus PDFs using a **Retrieval-Augmented Generation (RAG)** pipeline powered by Google Gemini and ChromaDB.

</div>

---

## 📌 Problem Statement Compliance (PS-02)

| PS-02 Core Requirement | Project Feature & Implementation | Status |
| :--- | :--- | :---: |
| **Natural Language Understanding** | Multi-turn conversational interface powered by LangChain & Gemini | ✅ **Met** |
| **Controlled Context Retrieval** | Vector search over local PDFs (`rtu 5th sem.pdf`) & `data.json` database | ✅ **Met** |
| **Role-Based Access Control** | Tailored portals for **Student**, **Faculty**, and **Staff / Admin** | ✅ **Met** |
| **Evidence Grounding (No Hallucinations)** | Outputs verified source tags (`data.json`, `rtu 5th sem.pdf`) for every answer | ✅ **Met** |
| **Autonomous Agent Planning** | Transparent workflow expansion showing exact reasoning steps and context scans | ✅ **Met** |
| **Zero-Downtime Fallback** | Deterministic JSON/PDF fallback parser when API limits or key constraints occur | ✅ **Met** |

---

## 🌟 Key Features & User Portals

### 👨‍🎓 1. Student Portal
* **Timetable & Schedules**: Instant lookup for daily class schedules, room numbers, and subject faculty.
* **Academic Calendar**: Real-time alerts for semester start dates, mid-term examinations, and end-term schedules.
* **Events & Hackathons**: Stay updated on campus events (e.g., *Arya National Hackathon*, *Annual TechFest Apex*).

### 👩‍🏫 2. Faculty Portal
* **Teaching Assignments**: View assigned subjects, laboratory slots, and assigned lecture halls.
* **Syllabus & Curriculum**: Query specific syllabus units across V and VI Semesters (CSE-AI).
* **Department Notices**: Access official academic notices and department notifications.

### 💼 3. Staff & Admin Portal
* **Operational Management**: Overview of overall academic calendars, faculty allocations, and venue bookings.
* **Knowledge Base Uploads**: Live uploading and indexing of new institutional circulars and syllabus updates into ChromaDB.

---



## 📁 Repository Structure

```text
.
├── app.py                   # Main Streamlit user interface & multi-portal router
├── agent.py                 # Core AI Helpdesk agent logic, Gemini integration & fallback handlers
├── knowledge.py             # RAG indexing, document chunking & ChromaDB retriever
├── indexer.py               # Document processing workflow
├── college_banner.jpg       # Main campus graphic header
├── data/
│   └── knowledge.json       # Structured college database (Timetables, Faculty, Events, Notices)
└── knowledge_base/
    ├── rtu 5th sem.pdf      # Official Rajasthan Technical University syllabus document
    └── Syllabus 3rd Year CSE(AI) V & VI Sem.pdf

```
---

## 🚀 Quickstart Guide

### Prerequisites
```text
Python 3.10 or higher
```

### Git

#### 1. Clone Repository
```text
Bash
git clone [https://github.com/AnamikaShah95/College_AI_Helpdesk.git](https://github.com/AnamikaShah95/College_AI_Helpdesk.git)
cd College_AI_Helpdesk
```
#### 2. Set Up Virtual Environment
```text
PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
#### 3. Install Dependencies
```text
Bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```text
Set your Google Gemini API key in your terminal session:
PowerShell
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
```

#### 5. Launch Application
```text
Bash
streamlit run app.py
```
---