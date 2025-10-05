import streamlit as st
from database import create_tables,add_admin
create_tables()  # ensures tables exist on startup
import sqlite3

def ensure_admin_exists():
    conn = sqlite3.connect("resume_system.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM admin WHERE username = ?", ("admin",))
    count = c.fetchone()[0]
    conn.close()

    if count == 0:
        add_admin("admin", "admin123")
        print("✅ Default admin created successfully (admin / admin123)")
    else:
        print("ℹ️ Admin already exists.")

# Run this on every app start
ensure_admin_exists()




st.set_page_config(
    page_title="AI Powered Resume Checker & Reviewer",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="collapsed"
)

# Custom CSS for a modern, clean, and interactive look
st.markdown(
    """
    <style>
        /* General Streamlit tweaks */
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
        .reportview-container .main .block-container {
            padding-top: 2rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
        }

        /* Hero Section Styling */
        .hero {
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(135deg, #e0f2f7, #bbdefb); /* Light gradient background */
            border-radius: 15px;
            margin-bottom: 3rem;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        .hero h1 {
            font-size: 3.2rem; /* Larger, more impactful title */
            color: #1a237e; /* Darker blue for prominence */
            margin-bottom: 0.75rem;
            line-height: 1.2;
        }
        .hero p {
            font-size: 1.3rem; /* Slightly larger text */
            color: #3f51b5; /* Blue-grey for readability */
            max-width: 800px;
            margin: 0.5rem auto 1.5rem auto;
            font-weight: 400;
        }
        .contributors {
            margin-top: 1.5rem;
            font-size: 1rem;
            color: #607d8b;
            font-weight: 500;
        }

        /* Feature Cards (replacing analytics) */
        .feature-container {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 3rem;
            flex-wrap: wrap; /* Allows cards to wrap on smaller screens */
            padding: 0 1rem;
        }
        .feature-card {
            background-color: white;
            padding: 2rem;
            border-radius: 12px;
            width: 300px; /* Fixed width for consistency */
            text-align: center;
            box-shadow: 0 6px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            border: 1px solid #e0e0e0;
        }
        .feature-card:hover {
            transform: translateY(-8px); /* More pronounced lift */
            box-shadow: 0 12px 25px rgba(0,0,0,0.15);
        }
        .feature-card img {
            width: 80px; /* Larger icons */
            height: 80px;
            margin-bottom: 1.5rem;
            border-radius: 50%; /* Make icons circular if desired */
            background-color: #e3f2fd; /* Light background for icon */
            padding: 10px;
        }
        .feature-card h3 {
            margin-bottom: 0.75rem;
            color: #1e88e5; /* Consistent blue for titles */
            font-size: 1.5rem;
        }
        .feature-card p {
            font-size: 1rem;
            color: #546e7a;
            line-height: 1.6;
        }

        /* Button Card Container */
        .button-card-container {
            display: flex;
            justify-content: center;
            gap: 3rem; /* Increased gap */
            margin-top: 4rem;
            flex-wrap: wrap;
        }
        .button-card {
            background-color: #ffffff;
            padding: 2.5rem 2rem; /* More padding */
            border-radius: 15px;
            width: 350px; /* Wider cards for buttons */
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
            border: 1px solid #d0d0d0;
            display: flex;
            flex-direction: column;
            justify-content: space-between; /* Space out content vertically */
        }
        .button-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        .button-card img {
            width: 90px; /* Larger icons for buttons */
            height: 90px;
            margin-bottom: 1.5rem;
            margin-left: auto;
            margin-right: auto;
            background-color: #c5e1a5; /* Light green background */
            padding: 12px;
            border-radius: 50%;
        }
        .button-card h3 {
            margin-bottom: 1rem;
            color: #388e3c; /* Green for action */
            font-size: 1.8rem;
        }
        .button-card p {
            font-size: 1.05rem;
            color: #555;
            margin-bottom: 2rem; /* Space before button */
            flex-grow: 1; /* Allow paragraph to take available space */
        }
        /* Style for Streamlit buttons inside the cards */
        .stButton button {
            background-color: #4CAF50 !important; /* Green button */
            color: white !important;
            border-radius: 8px !important;
            padding: 0.8rem 1.5rem !important;
            font-size: 1.1rem !important;
            width: 100%; /* Make buttons full width in card */
            border: none !important;
            box-shadow: 0 4px 10px rgba(76,175,80,0.4);
            transition: background-color 0.2s, transform 0.2s, box-shadow 0.2s;
        }
        .stButton button:hover {
            background-color: #388e3c !important; /* Darker green on hover */
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(76,175,80,0.5);
        }

        /* Footer Styling */
        .footer {
            margin-top: 5rem;
            padding: 1.5rem 1rem;
            text-align: center;
            font-size: 0.95rem;
            color: #78909c;
            background-color: #eceff1;
            border-top: 1px solid #cfd8dc;
            border-radius: 0 0 15px 15px; /* Match hero border radius */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Hero section
st.markdown(
    """
    <div class="hero">
        <h1>Automated Resume Relevance Check System</h1>
        <p>
            An AI-powered platform that intelligently matches resumes with job descriptions, 
            efficiently ranks applicants, and provides instant, personalized feedback. 
            Designed to streamline the recruitment process for both recruiters and candidates.
        </p>
        <div class="contributors">
            Developed by <b>Ajay Avale</b> & <b>Aditya Dengale</b> <br>
            Vishwakarma Institute of Technology, Pune
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h2 style='text-align: center; color: #1a237e; margin-top: 3rem; margin-bottom: 2rem;'>🚀 Why Choose Our AI Recruiter?</h2>", unsafe_allow_html=True)

# Feature cards (replacing graphs)
st.markdown(
    """
    <div class="feature-container">
        <div class="feature-card">
            <img src="https://cdn-icons-png.flaticon.com/512/8643/8643534.png" alt="AI Matching">
            <h3>Precision AI Matching</h3>
            <p>Our advanced AI algorithms meticulously compare resumes with job descriptions for an accurate fit, saving hours of manual review.</p>
        </div>
        <div class="feature-card">
            <img src="https://cdn-icons-png.flaticon.com/512/2921/2921216.png" alt="Feedback">
            <h3>Personalized Candidate Feedback</h3>
            <p>Candidates receive constructive, AI-generated feedback to improve their resumes, boosting their chances for future roles.</p>
        </div>
        <div class="feature-card">
            <img src="https://cdn-icons-png.flaticon.com/512/8627/8627685.png" alt="Efficiency">
            <h3>Boost Recruitment Efficiency</h3>
            <p>Automate your initial screening process, reduce time-to-hire, and allow your team to focus on strategic tasks.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h2 style='text-align: center; color: #1a237e; margin-top: 4rem; margin-bottom: 2rem;'>Start Your Journey Here</h2>", unsafe_allow_html=True)

# Cards with real Streamlit buttons
# Using st.columns for the layout of these cards to keep them aligned
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="button-card">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135680.png" alt="Jobs">
            <h3>📄 View Job Listings</h3>
            <p>Explore available opportunities and submit your resume for instant AI-powered evaluation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Go to Job Listings", key="view_jobs", use_container_width=True):
        st.switch_page("pages/Apply_Jobs.py")

with col2:
    st.markdown(
        """
        <div class="button-card">
            <img src="https://cdn-icons-png.flaticon.com/512/3064/3064197.png" alt="Admin">
            <h3>🔑 Admin Login</h3>
            <p>Recruiters can log in to manage job postings, screen resumes, and review applicants.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Go to Admin Login", key="admin_login", use_container_width=True):
        st.switch_page("pages/LoginForAdmin.py")

# Footer
st.markdown(
    """
    <div class="footer">
        🚀 Built for Hackathon | Powered by AI & Streamlit | 2025
    </div>
    """,
    unsafe_allow_html=True,
)