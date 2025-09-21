import streamlit as st
import os
from PyPDF2 import PdfReader
import docx
from sentence_transformers import SentenceTransformer, util

# Load embedding model (tiny for speed)
model = SentenceTransformer('all-MiniLM-L6-v2')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper: extract text
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return None

# Streamlit UI
st.set_page_config(page_title="Resume Relevance Checker", layout="wide")

st.title("📄 Automated Resume Relevance Checker")

# Section 1: Upload JD
st.header("Upload Job Description (JD)")
jd_file = st.file_uploader("Upload JD file (PDF/DOCX)", type=["pdf", "docx"])

# Section 2: Upload Resume
st.header("Upload Resume")
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

if jd_file and resume_file:
    jd_text = extract_text(jd_file)
    resume_text = extract_text(resume_file)

    if jd_text and resume_text:
        # Embeddings
        jd_embedding = model.encode(jd_text, convert_to_tensor=True)
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)

        # Similarity
        score = util.pytorch_cos_sim(resume_embedding, jd_embedding).item()
        relevance_score = round(score * 100, 2)

        # Verdict
        if relevance_score > 70:
            verdict = "✅ High Fit"
        elif relevance_score > 40:
            verdict = "⚠️ Medium Fit"
        else:
            verdict = "❌ Low Fit"

        # Output
        st.subheader("Results")
        st.metric("Relevance Score", f"{relevance_score}")
        st.write("Verdict:", verdict)

        st.subheader("JD Extract (Preview)")
        st.text(jd_text[:500] + "..." if len(jd_text) > 500 else jd_text)

        st.subheader("Resume Extract (Preview)")
        st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)

    else:
        st.error("Unsupported file format.")
