Resume Checker AI
A Streamlit-based web app that evaluates resumes against job descriptions using AI-powered semantic similarity and Gemini summarization. Built for hackathon use.
Features
1. Add and delete admin users
2. Upload and manage job descriptions
3. Upload resumes and calculate relevance score
4. Summarize job descriptions using Gemini AI
Verdict system: High Fit / Medium Fit / Low Fit

Requirements

1.Python 3.10+
2. Packages: Streamlit, PyPDF2, python-docx, sentence-transformers, langchain-google-genai, werkzeug

Install dependencies:

pip install -r requirements.txt

How to Run Locally
streamlit run Home.py

This will open the Home page in the browser where u can navigate 
If you want to log in as admin -> Enter username as admin1 or admin2 and password as root for both of them 
IF you want to check available jobs then go to Home->apply jobs, choose a job->apply->
