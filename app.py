import os
import streamlit as st
from agent import run_helpdesk
from auth import authenticate, get_demo_users

st.set_page_config(
    page_title="ARYA COLLEGE OF ENGINEERING | AI Helpdesk",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ORIGINAL PASTEL AESTHETIC STYLING ---
st.markdown("""
<style>
    /* Main Background - Soft Pastel Olive */
    .stApp {
        background-color: #F4F6F0 !important;
        color: #1A202C !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar Styling - Soft Sage Olive */
    section[data-testid="stSidebar"] {
        background-color: #E2E8D8 !important;
        border-right: 2px solid #D0E1FD !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #2D3748 !important;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #2D4430 !important;
        font-weight: 800 !important;
    }

    /* Header Styling */
    .college-header {
        text-align: center;
        color: #DC2626 !important;
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 5px;
        margin-bottom: 2px;
    }
    
    .college-subtitle {
        text-align: center;
        color: #4A5568 !important;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }

    /* ROLE SELECTION CARDS */
    .role-card-box {
        background-color: #FEF9C3 !important;
        border: 2px solid #BAE6FD !important;
        border-radius: 16px !important;
        padding: 24px !important;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
        margin-bottom: 15px !important;
    }
    
    .role-icon {
        font-size: 3rem;
        margin-bottom: 10px;
    }

    /* ALL VIBRANT PASTEL PINK BUTTONS */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        background-color: #F472B6 !important;
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        border: 2px solid #E11D48 !important;
        border-radius: 10px !important;
        box-shadow: 0 3px 6px rgba(244, 114, 182, 0.4) !important;
        padding: 8px 14px !important;
        transition: all 0.2s ease-in-out !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        height: auto !important;
    }
    
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        background-color: #FB7185 !important;
        color: #0F172A !important;
        border-color: #BE123C !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 10px rgba(251, 113, 133, 0.5) !important;
    }

    /* LOGIN FORM CONTAINER */
    div[data-testid="stForm"] {
        background-color: #FEF9C3 !important;
        border: 2px solid #BAE6FD !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }

    /* FORM INPUT FIELDS */
    div[data-baseweb="input"] {
        background-color: #F0F9FF !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] input {
        color: #0F172A !important;
        background-color: #F0F9FF !important;
        font-weight: 600 !important;
    }

    /* CHAT SURFACES (Pastel Yellow with Cyan Borders) */
    div[data-testid="stChatMessage"] {
        background-color: #FEF9C3 !important;
        border-radius: 14px !important;
        border: 2px solid #BAE6FD !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.04) !important;
        margin-bottom: 12px !important;
        padding: 14px !important;
    }

    div[data-testid="stChatMessage"] * {
        color: #1E293B !important;
        font-size: 0.98rem;
    }

    div[data-testid="stChatMessage"] code {
        background-color: #E0F2FE !important;
        color: #0369A1 !important;
        font-weight: 700 !important;
    }

    /* CHAT INPUT CONTAINER & TEXT AREA (Clean White Input Bar) */
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border-top: 2px solid #BAE6FD !important;
        padding-top: 10px !important;
    }

    div[data-testid="stChatInput"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 12px !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
    }

    div[data-testid="stChatInput"] button {
        background-color: #F472B6 !important;
        color: #0F172A !important;
        border-radius: 8px !important;
    }

    /* BADGES & TAGS */
    .role-badge {
        display: inline-block;
        background-color: #F472B6;
        color: #0F172A !important;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.82rem;
    }

    .source-tag {
        display: inline-block;
        background-color: #E0F2FE !important;
        color: #0369A1 !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        padding: 4px 10px;
        border-radius: 8px;
        margin-right: 6px;
        margin-top: 4px;
        border: 1px solid #7DD3FC;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to render campus image
def render_campus_banner():
    candidate_files = [f for f in os.listdir(".") if f.endswith((".jpeg", ".jpg", ".png")) and "WhatsApp" in f]
    img_found = candidate_files[0] if candidate_files else None
    
    if not img_found:
        for fname in ["campus.jpeg", "campus.jpg", "campus.png"]:
            if os.path.exists(fname):
                img_found = fname
                break
            
    if img_found:
        st.image(img_found, use_container_width=True)

# Session State Setup
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# --- AUTHENTICATION & ROLE SELECTION SCREEN ---
if st.session_state.user is None:
    st.markdown('<div class="college-header">ARYA COLLEGE OF ENGINEERING</div>', unsafe_allow_html=True)
    st.markdown('<div class="college-subtitle">🎓 AI Helpdesk Portal • Domain Verse 1.0</div>', unsafe_allow_html=True)
    
    render_campus_banner()

    if st.session_state.selected_role is None:
        st.markdown("<h3 style='text-align: center; color: #2D4430; margin-top: 15px;'>Select Your User Role to Continue</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="role-card-box">
                <div class="role-icon">👨‍🎓</div>
                <h3 style="color: #1E293B; margin-bottom: 5px;">Student Portal</h3>
                <p style="color: #475569; font-size: 0.9rem;">Access timetables, exams, academic calendar & campus events.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue as Student", key="btn_role_student", use_container_width=True):
                st.session_state.selected_role = "student"
                st.rerun()

        with col2:
            st.markdown("""
            <div class="role-card-box">
                <div class="role-icon">👩‍🏫</div>
                <h3 style="color: #1E293B; margin-bottom: 5px;">Faculty Portal</h3>
                <p style="color: #475569; font-size: 0.9rem;">Manage teaching schedules, department notices & syllabus updates.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue as Faculty", key="btn_role_faculty", use_container_width=True):
                st.session_state.selected_role = "faculty"
                st.rerun()

        with col3:
            st.markdown("""
            <div class="role-card-box">
                <div class="role-icon">👔</div>
                <h3 style="color: #1E293B; margin-bottom: 5px;">Staff & Admin</h3>
                <p style="color: #475569; font-size: 0.9rem;">Access helpdesk administration, circulars & operational tools.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue as Staff", key="btn_role_staff", use_container_width=True):
                st.session_state.selected_role = "staff"
                st.rerun()

    else:
        role_title = st.session_state.selected_role.capitalize()
        default_id = "student001" if st.session_state.selected_role == "student" else ("faculty001" if st.session_state.selected_role == "faculty" else "admin001")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("← Switch User Role", key="btn_back_role"):
                st.session_state.selected_role = None
                st.rerun()

            st.markdown(f"### 🔐 {role_title} Login")
            with st.form("login_form"):
                identifier = st.text_input("👤 Email / User ID", value=default_id)
                password = st.text_input("🔑 Password", type="password", value="demo123")
                submitted = st.form_submit_button(f"Sign In to {role_title} Portal", use_container_width=True)

                if submitted:
                    user = authenticate(identifier, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Try student001 / demo123")

            with st.expander("📌 Available Demo Accounts"):
                for u in get_demo_users():
                    st.caption(f"• **{u['role'].title()}**: `{u['identifier']}` / `demo123`")
    st.stop()

# --- MAIN DASHBOARD ---
user = st.session_state.user

with st.sidebar:
    st.markdown("## 🏫 Helpdesk Navigation")
    st.markdown(f"👤 **{user['name']}**")
    st.markdown(f"Role: <span class='role-badge'>{user['role'].title()}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📋 Profile Context")
    st.markdown(f"🏢 **Dept:** {user.get('department','—')}")
    if user["role"] == "student":
        st.markdown(f"📚 **Sem:** {user.get('semester','—')} | **Sec:** {user.get('section','—')}")
    
    # Document Upload Section
    if user["role"] in ["staff", "admin", "faculty"]:
        st.markdown("---")
        with st.expander("📤 Upload Knowledge Data", expanded=False):
            st.caption("Upload files directly to feed the helpdesk AI agent.")
            
            category = st.selectbox(
                "Select Document Category", 
                ["Timetables", "Academic Calendar", "Event Notices", "Syllabus / Notes"],
                key="sb_doc_category"
            )
            
            uploaded_files = st.file_uploader(
                "Choose files (PDF, CSV, TXT)", 
                type=["pdf", "csv", "txt", "xlsx"], 
                accept_multiple_files=True,
                key="file_uploader_main"
            )
            
            if st.button("📥 Upload & Ingest Data", use_container_width=True, key="btn_ingest_upload_data"):
                if uploaded_files:
                    save_dir = os.path.join(".", "knowledge_base")
                    os.makedirs(save_dir, exist_ok=True)
                    
                    saved_names = []
                    for file in uploaded_files:
                        file_path = os.path.join(save_dir, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        saved_names.append(file.name)
                    
                    st.success(f"Successfully uploaded {len(saved_names)} file(s) into **{category}**!")
                    st.toast("Files stored in `./knowledge_base/` ready for indexing!", icon="✅")
                else:
                    st.warning("Please choose at least one file before uploading.")

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    if user["role"] == "student":
        quick_queries = [
            "🗓️ When does V semester start?",
            "📅 What is my timetable?",
            "📍 What is the timetable for AI&DS Alpha on Monday?",
            "👨‍🏫 Who teaches CGM for AI&DS Alpha?",
            "🏆 What events are happening?",
            "📝 When is my DSA exam?"
        ]
    elif user["role"] == "faculty":
        quick_queries = [
            "🗓️ When does V semester start?",
            "📅 What is my timetable?",
            "📍 What is the timetable for AI&DS Alpha on Monday?",
            "👨‍🏫 Who teaches CGM for AI&DS Alpha?",
            "🏆 What events are happening?",
            "📝 When is my DSA exam?"
        ]
    else:
        quick_queries = [
            "📋 Show overall academic calendar",
            "🏆 What campus events are scheduled?",
            "🏢 Show faculty department assignments",
            "📢 What notices need distribution?",
            "📍 General timetable schedule"
        ]

    for idx, q in enumerate(quick_queries):
        clean_query = q.split(" ", 1)[1] if " " in q else q
        if st.button(q, key=f"qa_btn_{idx}_{clean_query[:10]}", use_container_width=True):
            st.session_state.pending_query = clean_query

    st.markdown("---")
    if st.button("🗑️ Clear Chat", key="btn_clear_chat_history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout", key="btn_logout_user_session", use_container_width=True):
        st.session_state.user = None
        st.session_state.selected_role = None
        st.session_state.messages = []
        st.rerun()

# Dashboard Banner & Header
st.markdown('<div class="college-header">ARYA COLLEGE OF ENGINEERING</div>', unsafe_allow_html=True)
st.markdown('<div class="college-subtitle">🎓 AI-Powered College Helpdesk Companion</div>', unsafe_allow_html=True)

render_campus_banner()

# Render Message History
for role, message in st.session_state.messages:
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**{message}**")
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["answer"])
            
            if message.get("sources"):
                st.markdown("**Verified Evidence Sources:**")
                src_html = "".join([f'<span class="source-tag">📌 {src}</span>' for src in message["sources"]])
                st.markdown(src_html, unsafe_allow_html=True)
            
            if message.get("statuses"):
                with st.expander("⚙️ View Autonomous Agent Planning Workflow"):
                    for status in message["statuses"]:
                        if "Replanning" in status or "Broadening" in status:
                            st.markdown(f"🔴 `{status}`")
                        elif "Verified" in status:
                            st.markdown(f"🟢 `{status}`")
                        elif "Searching" in status:
                            st.markdown(f"🟡 `{status}`")
                        else:
                            st.markdown(f"🔵 `{status}`")

# Handle Quick Action or Chat Input
prompt = st.chat_input("Ask a question about academic calendar, timetable, faculty, or events...")

if st.session_state.pending_query:
    prompt = st.session_state.pending_query
    st.session_state.pending_query = None

if prompt:
    st.session_state.messages.append(("user", prompt))
    with st.spinner("Agent planning and searching controlled sources..."):
        result = run_helpdesk(prompt, user, st.session_state.messages)
    st.session_state.messages.append(("assistant", result))
    st.rerun()