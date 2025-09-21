import streamlit as st
from database import add_jd, get_all_jds
from PyPDF2 import PdfReader
import docx
import os
from datetime import datetime
import pandas as pd 

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Check if admin is logged in
if "admin_logged_in" not in st.session_state or not st.session_state.admin_logged_in:
    st.warning("Please login first!")
    st.stop()  # Stop loading dashboard if not logged in

# Helper: Extract text from JD
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

# Admin Dashboard
st.title("Admin Dashboard")
st.subheader("Upload Job Description (JD)")

jd_file = st.file_uploader("Select JD file (PDF/DOCX)", type=["pdf", "docx"], key="jd_upload")
jd_title = st.text_input("Job Title", "")

if st.button("Upload JD"):
    if jd_file and jd_title:
        # Save file
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{jd_file.name}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(jd_file.getbuffer())

        # Extract text
        jd_text = extract_text(jd_file)
        if jd_text:
            # Save to DB
            add_jd(jd_title, jd_text, filename)
            st.success(f"JD '{jd_title}' uploaded successfully!")
        else:
            st.error("Could not extract text from the file.")

# List all uploaded JDs
st.subheader("Uploaded Job Descriptions")
jds = get_all_jds()
if jds:
    jds_subset = [(row[0], row[1]) for row in jds]
    df=pd.DataFrame(
        jds_subset,
        columns=["JD ID","Title"]
    )
    st.write("Uploaded JD's📊")
    st.dataframe(df)
else:
    st.info("No JDs uploaded yet.")
