import streamlit as st
from database import get_all_jds
import os

st.set_page_config(page_title="Welcome to AI Powered Resume Checker and Reviewer", 
                   layout="centered", 
                   initial_sidebar_state="collapsed")

# Hide sidebar and add custom CSS for card styling
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
        
        .job-card {
            background-color: #f0f2f6; /* Light gray background */
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            border: 1px solid #e0e0e0; /* Subtle border */
        }
        .job-card:hover {
            transform: translateY(-5px); /* Lift effect on hover */
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.12);
        }
        .job-card h3 {
            color: #1f77b4; /* A nice blue for the title */
            margin-top: 0;
            margin-bottom: 5px;
        }
        .job-card p {
            color: #666;
            font-size: 14px;
            margin-bottom: 0;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 16px;
            border: none;
            cursor: pointer;
            transition: background-color 0.2s ease-in-out;
        }
        .stButton button:hover {
            background-color: #388e3c;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Available Jobs / Apply")

# Fetch all jobs
jobs = get_all_jds()

if not jobs:
    st.warning("No jobs available yet.")
    st.stop()

# Initialize session state to track selected job
if "selected_jd_id" not in st.session_state:
    st.session_state.selected_jd_id = None

# Show job cards with an integrated button
st.subheader("Explore Opportunities")
for jd in jobs:
    jd_id, jd_title, jd_desc = jd
    
    # Use st.container to group the markdown card and button
    with st.container():
        # Display the custom-styled markdown card
        st.markdown(
            f"""
            <div class="job-card">
                <h3>{jd_title}</h3>
                <p>Click "View Details" to see the full description and apply.</p>
            </div>
            """, unsafe_allow_html=True
        )
        # Place the Streamlit button logically under the markdown card
        if st.button(f"View Details →", key=f"apply_{jd_id}"):
            st.session_state.selected_jd_id = jd_id
            st.switch_page("pages/jobDesc.py")

