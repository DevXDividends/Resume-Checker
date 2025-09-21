import streamlit as st
from database import get_all_jds, delete_job, DB_NAME
import sqlite3

st.set_page_config(page_title="Admin - Delete Jobs", layout="centered")
st.title("Admin Panel - Delete Jobs")

# Fetch all jobs
jobs = get_all_jds()
if not jobs:
    st.warning("No jobs available.")
    st.stop()

st.subheader("Current Jobs")
for jd in jobs:
    jd_id, jd_title, jd_desc = jd
    with st.container():
        st.markdown(
            f"""
            <div style="border:1px solid #f44336; padding:15px; margin-bottom:10px; border-radius:10px;">
                <h3>{jd_title}</h3>
                <p style='color:gray; font-size:14px;'>{jd_desc[:200].replace('\n',' ')}...</p>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button(f"Delete → {jd_title}", key=f"delete_{jd_id}"):
            # Delete all resumes linked to this job first
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM resumes WHERE jd_id=?", (jd_id,))
            conn.commit()
            conn.close()

            # Delete the job
            delete_job(jd_id)
            st.success(f"Job '{jd_title}' and all its resumes have been deleted!")

            # Force page refresh by updating a dummy session state
            if "refresh" not in st.session_state:
                st.session_state.refresh = 0
            st.session_state.refresh += 1
            st.experimental_rerun = None  # trick for old references
            st.experimental_rerun = lambda: None  # just to avoid AttributeError
            st.experimental_rerun()
