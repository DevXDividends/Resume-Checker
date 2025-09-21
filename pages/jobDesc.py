import streamlit as st
from database import get_job_by_id, add_resume
from PyPDF2 import PdfReader
import docx
import os
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv


# Initialize Gemini
gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key="AIzaSyAv3YjDlwDxzBGQE4PJLmMJ1nsPVasnmMY"
)

# Page config
st.set_page_config(
    page_title="Job Description & Apply",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load embeddings model (cached)
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# Helper: extract text from resume (cached)
@st.cache_data
def extract_text(file_bytes, filename):
    if filename.endswith(".pdf"):
        reader = PdfReader(file_bytes)
        return "".join([page.extract_text() or "" for page in reader.pages])
    elif filename.endswith(".docx"):
        doc = docx.Document(file_bytes)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return None

# Show job description & upload form
def show_job(jd_id):
    job = get_job_by_id(jd_id)
    if not job:
        st.error("Job not found")
        return
    
    jd_id, jd_title, jd_desc = job
    st.title(jd_title)

    # Cache JD embedding
    if f"jd_emb_{jd_id}" not in st.session_state:
        with st.spinner("Encoding job description..."):
            st.session_state[f"jd_emb_{jd_id}"] = model.encode(jd_desc, convert_to_tensor=True)

    jd_emb = st.session_state[f"jd_emb_{jd_id}"]

    # Lazy Gemini summarization
    if f"job_desc_{jd_id}" not in st.session_state:
        if st.button("Generate Simplified Job Description", key=f"summarize_{jd_id}"):
            with st.spinner("Summarizing with Gemini..."):
                response = gemini.invoke(f"Summarize for students:\n{jd_desc}")
                st.session_state[f"job_desc_{jd_id}"] = response.content

    if f"job_desc_{jd_id}" in st.session_state:
        st.subheader("Job Description (Simplified)")
        st.write(st.session_state[f"job_desc_{jd_id}"])
    else:
        st.subheader("Job Description")
        st.write(jd_desc)

    # Candidate input
    candidate_name = st.text_input("Your Name", key=f"name_{jd_id}")
    resume_file = st.file_uploader(
        "Upload Resume (PDF/DOCX)", type=["pdf", "docx"], key=f"upload_{jd_id}"
    )

    if st.button("Check Relevance / Apply", key=f"check_{jd_id}"):
        if not candidate_name:
            st.warning("Enter your name")
        elif not resume_file:
            st.warning("Upload your resume")
        else:
            # Save resume file
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{resume_file.name}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(resume_file.getbuffer())

            # Extract text
            with st.spinner("Extracting text from resume..."):
                resume_text = extract_text(resume_file, resume_file.name)

            if not resume_text:
                st.error("Could not extract text from resume")
                return

            # Semantic similarity
            with st.spinner("Calculating relevance score..."):
                resume_emb = model.encode(resume_text, convert_to_tensor=True)
                score = util.pytorch_cos_sim(resume_emb, jd_emb).item()
                relevance_score = round(score * 100, 2)

            if relevance_score > 70:
                verdict = "✅ High Fit"
            elif relevance_score > 40:
                verdict = "⚠️ Medium Fit"
            else:
                verdict = "❌ Low Fit"

            # Save to database
            add_resume(candidate_name, jd_id, resume_text, filename, relevance_score, verdict)

            st.subheader("Results")
            st.metric("Relevance Score", f"{relevance_score}")
            st.write("Verdict:", verdict)
            st.success("Your resume has been evaluated and saved!")

# Auto-run if job is set in session_state
if "selected_jd_id" in st.session_state and st.session_state.selected_jd_id:
    show_job(st.session_state.selected_jd_id)
else:
    st.warning("No job selected. Go back to Apply Jobs page.")
