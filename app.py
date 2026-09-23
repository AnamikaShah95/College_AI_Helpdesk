import streamlit as st
from agent import run_helpdesk
from auth import authenticate, get_demo_users

st.set_page_config(page_title="College AI Helpdesk", page_icon="🎓", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.user is None:
    st.title("🎓 College AI Helpdesk")
    st.caption("Domain Verse 1.0 • Agentic AI Track")

    with st.form("login"):
        identifier = st.text_input("Email / Student ID / Faculty ID / Staff ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = authenticate(identifier, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials.")

    with st.expander("Demo accounts"):
        for u in get_demo_users():
            st.write(f"{u['role'].title()}: `{u['identifier']}` / `demo123`")
    st.stop()

user = st.session_state.user

with st.sidebar:
    st.title("College Helpdesk")
    st.write(f"**{user['name']}**")
    st.write(f"Role: {user['role'].title()}")
    st.write(f"Department: {user.get('department','—')}")
    if user["role"] == "student":
        st.write(f"Semester: {user.get('semester','—')}")
        st.write(f"Section: {user.get('section','—')}")

    st.divider()
    st.subheader("Quick Actions")
    quick = [
        "When does V semester start?",
        "Show the academic calendar for V semester.",
        "What is my timetable?",
        "Who teaches my DSA class?",
        "When is my DSA exam?",
    ]
    for q in quick:
        if st.button(q, use_container_width=True):
            st.session_state.messages.append(("user", q))
            result = run_helpdesk(q, user, st.session_state.messages)
            st.session_state.messages.append(("assistant", result))
            st.rerun()

    st.divider()
    if st.button("New Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

st.title("AI College Helpdesk")
st.caption("Ask about the academic calendar, syllabus, timetable, faculty, exams, notices and other verified college information.")

for role, message in st.session_state.messages:
    if role == "user":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.markdown(message["answer"])
            if message.get("sources"):
                st.markdown("**Sources**")
                for source in message["sources"]:
                    st.caption(f"• {source}")
            if message.get("statuses"):
                with st.expander("Agent status"):
                    for status in message["statuses"]:
                        st.write(status)

prompt = st.chat_input("Ask your college question...")
if prompt:
    st.session_state.messages.append(("user", prompt))
    with st.spinner("Agent is working..."):
        result = run_helpdesk(prompt, user, st.session_state.messages)
    st.session_state.messages.append(("assistant", result))
    st.rerun()
