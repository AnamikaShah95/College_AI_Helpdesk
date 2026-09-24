import os
import json
import glob
import re
from typing import List, Tuple, Dict, Any

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Load environment variables from .env file automatically
load_dotenv()

# Set Gemini API Key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

GREETINGS = {"hi", "hello", "hey", "good morning", "good evening", "greetings", "help", "who are you"}
CONFIDENCE_THRESHOLD = 0.25  # Calibrated Cosine Similarity threshold for all-MiniLM-L6-v2

# Global embedding model initialization (lightweight & fast)
EMBEDDINGS = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Global vector store cache to prevent re-indexing on every query
_VECTOR_STORE_CACHE = None


def extract_pages_from_pdf(file_path: str) -> List[Tuple[int, str]]:
    """Extracts raw text page-by-page from a PDF file using pypdf and joins single line breaks into complete paragraphs."""
    pages_content = []
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        for page_idx, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                # Fix line breaks: Replace single newlines with spaces while keeping paragraph gaps
                cleaned = re.sub(r'(?<!\n)\n(?!\n)', ' ', extracted)
                # Collapse multi-spaces into single spaces
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                pages_content.append((page_idx + 1, cleaned))
    except Exception as e:
        pages_content.append((1, f"[Error reading PDF: {e}]"))
    return pages_content


def read_and_chunk_knowledge_base(kb_dir: str) -> Tuple[List[Document], List[str], Dict[str, Any]]:
    """Scans knowledge base and breaks content into page-attributed semantic chunks."""
    documents = []
    sources = []
    json_data = {}

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )

    if os.path.exists(kb_dir):
        # 1. Process Structured JSON Data
        for file_path in glob.glob(os.path.join(kb_dir, "*.json")):
            fname = os.path.basename(file_path)
            sources.append(fname)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    json_data.update(data)
                    doc = Document(
                        page_content=json.dumps(data, indent=2),
                        metadata={"source": fname, "page": "N/A", "type": "structured_json"}
                    )
                    documents.append(doc)
            except Exception:
                pass

        # 2. Process PDFs Page by Page (Enables Page-Level Attribution)
        for file_path in glob.glob(os.path.join(kb_dir, "*.pdf")):
            fname = os.path.basename(file_path)
            sources.append(fname)
            page_list = extract_pages_from_pdf(file_path)
            for page_num, raw_text in page_list:
                chunks = text_splitter.split_text(raw_text)
                for chunk in chunks:
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={"source": fname, "page": page_num, "type": "pdf"}
                        )
                    )

        # 3. Process TXT & CSV Files
        for ext in ("*.txt", "*.csv"):
            for file_path in glob.glob(os.path.join(kb_dir, ext)):
                fname = os.path.basename(file_path)
                sources.append(fname)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read().strip()
                        cleaned_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
                        chunks = text_splitter.split_text(cleaned_text)
                        for chunk in chunks:
                            documents.append(
                                Document(
                                    page_content=chunk,
                                    metadata={"source": fname, "page": 1, "type": "text"}
                                )
                            )
                except Exception:
                    pass

    return documents, sources, json_data


def check_structured_json_match(query: str, json_data: dict) -> str:
    """Checks structured JSON data for direct hits like timetables or academic calendars."""
    q = query.lower().strip()

    if any(k in q for k in ["timetable", "schedule", "class", "monday", "slot"]):
        tt = json_data.get("timetables", {}).get("AI_DS_Alpha", {}).get("Monday", [])
        if tt:
            lines = ["### 🗓 Monday Timetable (AI&DS Alpha)\n"]
            lines.append("| Time Slot | Subject | Faculty | Room / Venue |")
            lines.append("|---|---|---|---|")
            for slot in tt:
                lines.append(f"| {slot.get('time')} | {slot.get('subject')} | {slot.get('faculty')} | {slot.get('room')} |")
            return "\n".join(lines)

    if any(k in q for k in ["semester", "start", "calendar", "exam"]):
        cal = json_data.get("academic_calendar", {})
        if cal:
            return (
                "### 📅 Academic Calendar Highlights\n\n"
                f"- **V Semester Start**: {cal.get('V_semester_start', 'N/A')}\n"
                f"- **Mid-Term Exams**: {cal.get('mid_term_exams', 'N/A')}\n"
                f"- **End-Term Exams**: {cal.get('end_term_exams', 'N/A')}\n"
                f"- **Overall Schedule**: {cal.get('overall_schedule', 'N/A')}"
            )

    return ""


def get_or_create_vector_store(documents: List[Document]) -> Chroma:
    """Creates or reuses in-memory Chroma vector index with explicit Cosine metric."""
    global _VECTOR_STORE_CACHE
    if _VECTOR_STORE_CACHE is None:
        _VECTOR_STORE_CACHE = Chroma.from_documents(
            documents,
            EMBEDDINGS,
            collection_metadata={"hnsw:space": "cosine"}
        )
    return _VECTOR_STORE_CACHE


def retrieve_with_confidence(query: str, vector_store: Chroma, k: int = 4) -> Tuple[List[Document], float]:
    """Retrieves top k chunks along with normalized confidence score."""
    try:
        results_with_scores = vector_store.similarity_search_with_relevance_scores(query, k=k)
    except Exception:
        results = vector_store.similarity_search(query, k=k)
        return results, 0.50

    if not results_with_scores:
        return [], 0.0

    matched_docs = [doc for doc, score in results_with_scores]
    
    # Extract max score and clamp between 0.00 and 1.00
    scores = [score for _, score in results_with_scores]
    max_confidence = max(scores) if scores else 0.0
    max_confidence = max(0.0, min(1.0, max_confidence))

    return matched_docs, max_confidence


def generate_escalation_ticket(user: dict, query: str, confidence_score: float) -> str:
    """Generates an administrative helpdesk ticket when knowledge base context is insufficient."""
    return (
        f"\n\n---\n"
        f"### 🎫 Support Ticket Escalation Draft\n"
        f"Since this inquiry was not resolved with high confidence in the official document repository, "
        f"you can submit the following ticket to the Department Helpdesk:\n\n"
        f"```text\n"
        f"Ticket ID : HD-{abs(hash(query)) % 100000:05d}\n"
        f"Student   : {user.get('name', 'Anonymous')} ({user.get('role', 'student').title()})\n"
        f"Dept      : {user.get('department', 'General')}\n"
        f"Inquiry   : \"{query}\"\n"
        f"KB Match  : Low Confidence ({confidence_score:.2f})\n"
        f"Status    : Pending Administrative Review\n"
        f"```\n"
        f"*Click below to forward this query directly to the Head of Department.*"
    )


def run_helpdesk(query: str, user: dict, history: list) -> dict:
    clean_query = query.strip().lower()

    # 1. GREETING GUARDRAIL
    if clean_query in GREETINGS or len(clean_query) <= 2:
        user_name = user.get("name", "User")
        role = user.get("role", "student").title()
        return {
            "answer": (
                f"Hello **{user_name}**! 👋 Welcome to the **Arya College AI Helpdesk** ({role} Portal).\n\n"
                "I am ready to help you with information from all uploaded department files and documents. "
                "Ask me any question regarding timetables, syllabus, notes, or academic guidelines!"
            ),
            "sources": [],
            "statuses": ["🟢 Handled via Conversational Router"]
        }

    # 2. VECTOR DB INGESTION & SCANNING
    statuses = ["Scanning `./knowledge_base/` for files..."]
    documents, all_sources, json_data = read_and_chunk_knowledge_base("./knowledge_base")
    statuses.append(f"Indexed {len(all_sources)} source file(s) into {len(documents)} page-attributed chunks.")

    # Step 2a: Check Structured JSON first
    json_match = check_structured_json_match(query, json_data)
    if json_match:
        return {
            "answer": json_match,
            "sources": ["data.json"],
            "statuses": statuses + ["🟢 Handled via Structured JSON Matcher"]
        }

    if not documents:
        return {
            "answer": "> ⚠️ **Note:** No knowledge base files were found in `./knowledge_base/`. Please upload relevant documents.",
            "sources": [],
            "statuses": statuses
        }

    # 3. VECTOR SEMANTIC SEARCH
    statuses.append("Building/Fetching in-memory Chroma Vector Index...")
    vector_store = get_or_create_vector_store(documents)

    statuses.append("Performing Vector Search with Page-Level Attribution...")
    retrieved_docs, confidence_score = retrieve_with_confidence(query, vector_store, k=4)
    statuses.append(f"Vector Search Complete. Peak Confidence Score: **{confidence_score:.2f}**")

    # Format Page-Specific Sources (e.g., "AOA UNIT - II.pdf (Page 3)")
    formatted_sources = []
    for doc in retrieved_docs:
        src = doc.metadata.get("source", "Unknown")
        pg = doc.metadata.get("page")
        src_str = f"{src} (Page {pg})" if pg and pg != "N/A" else src
        if src_str not in formatted_sources:
            formatted_sources.append(src_str)

    # 4. LLM GENERATION WITH PAGE CITATIONS & TICKET ESCALATION
    if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 10:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            statuses.append("Synthesizing answer using Gemini AI...")
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=GEMINI_API_KEY)

            # Clean newlines beforehand to avoid backslash inside f-string expression
            context_blocks = []
            for doc in retrieved_docs:
                clean_content = doc.page_content.replace("\n", " ")
                src_info = f"Source [{doc.metadata.get('source')} - Page {doc.metadata.get('page')}]:\n{clean_content}"
                context_blocks.append(src_info)
            context_str = "\n\n".join(context_blocks)

            if confidence_score >= CONFIDENCE_THRESHOLD:
                prompt = f"""
                You are the official AI Helpdesk Assistant for Arya College of Engineering.
                User Details: Name: {user.get('name')}, Role: {user.get('role')}, Dept: {user.get('department')}

                RETRIEVED DOCUMENT CONTEXT (Confidence: {confidence_score:.2f}):
                {context_str}

                USER QUERY: {query}

                INSTRUCTIONS:
                - Answer the user query using ONLY the provided document context.
                - Write your output in continuous, well-formed paragraphs and lists. Never split a single sentence into multiple lines.
                - Format your answer clearly using Markdown (bullet points, bold text, or tables where appropriate).
                - Explicitly cite the document name AND page number when referencing facts (e.g., "[AOA UNIT - II.pdf, Page 4]").
                """
                res = llm.invoke(prompt)
                answer_content = res.content
            else:
                prompt = f"""
                You are the official AI Helpdesk Assistant for Arya College of Engineering.
                User Details: Name: {user.get('name')}, Role: {user.get('role')}, Dept: {user.get('department')}

                USER QUERY: {query}

                INSTRUCTIONS:
                - Start your response with this exact banner at the top:
                  "> ⚠️ **Note:** Information regarding **\"{query}\"** was **not found with high confidence in the uploaded knowledge base** (Relevance Score: {confidence_score:.2f}). Answering using general AI knowledge:"
                - Provide a concise general answer. Write in clean, complete paragraphs without awkward line breaks.
                """
                res = llm.invoke(prompt)
                answer_content = res.content + generate_escalation_ticket(user, query, confidence_score)

            return {
                "answer": answer_content,
                "sources": formatted_sources if confidence_score >= CONFIDENCE_THRESHOLD else all_sources,
                "statuses": statuses
            }
        except Exception as err:
            statuses.append(f"Gemini API call failed ({str(err)}). Falling back to structured vector summary.")

    # 5. LOCAL VECTOR SUMMARY FALLBACK
    if confidence_score >= CONFIDENCE_THRESHOLD:
        fallback_blocks = []
        for doc in retrieved_docs:
            clean_content = doc.page_content.replace("\n", " ").strip()
            fallback_blocks.append(f"- **[{doc.metadata.get('source')} - Page {doc.metadata.get('page')}]**: {clean_content}")
        
        formatted_chunks = "\n\n".join(fallback_blocks)
        answer = (
            f"### 📄 Vector Matched Documents (Confidence: `{confidence_score:.2f}`)\n\n"
            f"**Retrieved Content Chunks for \"{query}\":**\n\n"
            f"{formatted_chunks}"
        )
    else:
        answer = (
            f"> ⚠️ **Note:** Information regarding **\"{query}\"** was **not found in the uploaded knowledge base** "
            f"(Confidence Score: `{confidence_score:.2f}` below threshold `{CONFIDENCE_THRESHOLD}`).\n\n"
            f"Please verify that the document is uploaded or rephrase your query."
        ) + generate_escalation_ticket(user, query, confidence_score)

    return {
        "answer": answer,
        "sources": formatted_sources if confidence_score >= CONFIDENCE_THRESHOLD else all_sources,
        "statuses": statuses
    }