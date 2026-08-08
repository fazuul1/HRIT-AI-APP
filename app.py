import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="HRIT Assistant Hub", page_icon="🏥", layout="centered")

HRIT_SYSTEM_PROMPT = """
You are an expert AI Assistant specialized in Health Records and Information Technology (HRIT), Health Informatics, and Health Data Management.
Your core capabilities include:
1. Assisting with medical classification systems (ICD-10, ICD-11) and coding guidelines.
2. Explaining health records workflow, filing systems, and retrieval latency concepts.
3. Helping structure academic research papers, reports, and literature reviews in health information science.
4. Guiding health data analytics queries using Excel, SQL, and Python.
5. Providing engaging study summaries, quizzes, and project ideas for HRIT students.
Keep answers clear, highly structured, well-formatted, and student-friendly.
"""

# ---------------------------------------------------------
# 1. INITIALS LOGIN SYSTEM
# ---------------------------------------------------------
if "user_initials" not in st.session_state:
    st.session_state.user_initials = None

if not st.session_state.user_initials:
    st.title("🏥 HRIT Student AI Hub")
    st.markdown("Welcome! Please enter your initials to log in to the workspace.")
    
    initials_input = st.text_input("Student Initials (e.g., FM, JM, AK):", max_chars=4).strip().upper()
    
    if st.button("Log In to HRIT Hub"):
        if initials_input:
            st.session_state.user_initials = initials_input
            st.rerun()
        else:
            st.warning("Please enter your initials to enter.")
    st.stop()

# ---------------------------------------------------------
# 2. MAIN APPLICATION INTERFACE
# ---------------------------------------------------------
st.title("🏥 HRIT Research & Study Assistant")
st.caption(f"Logged in as Student: **{st.session_state.user_initials}** | Health Records & IT Workspace")

# Sidebar navigation & information
with st.sidebar:
    st.markdown("### 👤 Active Student")
    st.write(f"**Initials:** `{st.session_state.user_initials}`")
    if st.button("Log Out"):
        st.session_state.user_initials = None
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 📚 HRIT Quick Topics")
    st.markdown("- 📋 **ICD Coding Assistance**")
    st.markdown("- 📁 **Health Records Management**")
    st.markdown("- 📊 **Health Data Analytics (SQL/Excel)**")
    st.markdown("- 📝 **Research Project Helper**")

# ---------------------------------------------------------
# 3. AI ENGINE CONFIGURATION
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key missing! Please add `GEMINI_API_KEY` in Streamlit secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=HRIT_SYSTEM_PROMPT
)

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render past chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input(f"Ask a health records or research question, {st.session_state.user_initials}..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing HRIT query..."):
            try:
                # Rebuild history for context maintenance
                chat_history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error processing request: {e}")
