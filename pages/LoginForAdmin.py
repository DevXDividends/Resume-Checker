import streamlit as st
from database import verify_admin, create_tables

# Ensure tables exist
create_tables()
st.set_page_config(page_title="Welcome to AI Powered Resume Checker and Reviewer", 
                   layout="centered", 
                   initial_sidebar_state="collapsed")

# Hide sidebar completely + the collapse button
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

st.title("Admin Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if verify_admin(username, password):
        st.session_state.admin_logged_in = True
        st.success("Login successful! Redirecting to dashboard...")
        st.switch_page("pages/adminDashboard.py")  # Refresh page to load dashboard
    else:
        st.error("Invalid username or password")