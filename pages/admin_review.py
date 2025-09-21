import streamlit as st
import sqlite3
import shutil
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from database import DB_NAME
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()  # load from .env


# --- GEMINI API KEY ---


# Initialize Gemini
gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,  # deterministic output
    google_api_key="AIzaSyAv3YjDlwDxzBGQE4PJLmMJ1nsPVasnmMY"
)

# --- Streamlit config ---
st.set_page_config(page_title="Admin - Review Candidates", layout="centered")
st.title("Admin Panel - Candidate Evaluation")

# --- Ensure downloads folder exists ---
os.makedirs("downloads", exist_ok=True)

# --- Load SentenceTransformer model ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# --- DB Helpers ---
def update_feedback_in_db(resume_id, feedback_text):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE resumes SET feedback=? WHERE id=?", (feedback_text, resume_id))
    conn.commit()
    conn.close()

def get_download_file(candidate_name, original_filename):
    ext = os.path.splitext(original_filename)[1] or ".docx"
    output_file = f"downloads/{candidate_name.replace(' ','_')}{ext}"
    shutil.copy(f"uploads/{original_filename}", output_file)
    return output_file

# --- Gemini Feedback Helper with caching ---
def get_cached_feedback(resume_id, resume_text, jd_text):
    key = f"feedback_{resume_id}"
    if key not in st.session_state:
        try:
            prompt = f"""
            Resume Text: {resume_text}
            Job Description: {jd_text}
            Task: Identify missing skills, certifications, and projects. 
            Give 3-5 concise bullet points for improvement.
            """
            response = gemini.invoke(prompt)
            st.session_state[key] = response.content or "Feedback not available."
        except Exception as e:
            st.session_state[key] = "Feedback not available."
            st.warning(f"Feedback generation failed: {e}")
    return st.session_state[key]

# --- Select Job ---
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("SELECT id, title FROM job_descriptions ORDER BY upload_date DESC")
jobs = c.fetchall()
conn.close()

if not jobs:
    st.warning("No jobs available.")
    st.stop()

job_options = {f"{title}": jd_id for jd_id, title in jobs}
selected_job = st.selectbox("Select Job", list(job_options.keys()))
jd_id = job_options[selected_job]

# --- Fetch resumes ---
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("""
SELECT resumes.id, candidate_name, score, verdict, resumes.filename, 
       resumes.upload_date, resume_text, job_descriptions.description, feedback
FROM resumes
JOIN job_descriptions ON resumes.jd_id = job_descriptions.id
WHERE jd_id=?
ORDER BY score DESC, resumes.upload_date DESC
""", (jd_id,))
resumes = c.fetchall()
conn.close()

if not resumes:
    st.warning("No candidates have applied yet for this job.")
    st.stop()

# --- Remove duplicates (keep first/highest score) ---
unique_resumes = []
seen = set()
for r in resumes:
    name = r[1]
    if name not in seen:
        unique_resumes.append(r)
        seen.add(name)

# --- Categorize by verdict ---
high_fit, medium_fit, low_fit = [], [], []

for r in unique_resumes:
    resume_id, name, hard_score, verdict, filename, upload_date, resume_text, jd_text, feedback = r

    # Semantic similarity
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    semantic_score = util.pytorch_cos_sim(resume_emb, jd_emb).item() * 100

    final_score = 0.6 * hard_score + 0.4 * semantic_score

    if final_score >= 70:
        final_verdict = "✅ High Fit"
        high_fit.append((resume_id, name, final_score, final_verdict, filename, resume_text, jd_text, feedback))
    elif final_score >= 50:
        final_verdict = "⚠️ Medium Fit"
        medium_fit.append((resume_id, name, final_score, final_verdict, filename, resume_text, jd_text, feedback))
    else:
        final_verdict = "❌ Low Fit"
        low_fit.append((resume_id, name, final_score, final_verdict, filename, resume_text, jd_text, feedback))

# --- Display candidates ---
def display_candidates(category_name, candidates):
    st.markdown(f"### {category_name} ({len(candidates)})")
    for idx, cand in enumerate(candidates):
        resume_id, name, score, verdict, filename, resume_text, jd_text, feedback = cand

        # Use cached feedback
        if not feedback or feedback == "Feedback not available.":
            feedback = get_cached_feedback(resume_id, resume_text, jd_text)
            update_feedback_in_db(resume_id, feedback)

        st.markdown(
            f"""
            <div style="border:2px solid #4CAF50; padding:10px; margin-bottom:10px; border-radius:8px;">
                <b>Name:</b> {name}<br>
                <b>Relevance Score:</b> {score:.2f}%<br>
                <b>Verdict:</b> {verdict}<br>
                <b>Suggestions:</b>
                <ul>{''.join(f'<li>{line}</li>' for line in feedback.splitlines() if line.strip())}</ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        download_file = get_download_file(name, filename)
        st.download_button(
            label=f"Download Resume - {name}",
            data=open(download_file, "rb").read(),
            file_name=f"{name.replace(' ','_')}{os.path.splitext(filename)[1]}",
            mime="application/octet-stream",
            key=f"{name}_{idx}"
        )

# --- Display all categories ---
display_candidates("High Fit Candidates", high_fit)
display_candidates("Medium Fit Candidates", medium_fit)
display_candidates("Low Fit Candidates", low_fit)
