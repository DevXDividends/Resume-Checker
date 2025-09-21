import streamlit as st
import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "resume_system.db"  # matches your database

# ---------------- Database Helper Functions ----------------
def add_admin_db(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_admin_db(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def get_all_admins_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM admin")
    admins = [row[0] for row in cursor.fetchall()]
    conn.close()
    return admins

# ---------------- Streamlit Page ----------------
st.set_page_config(
    page_title="Manage Admins",
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

st.title("Manage Admins")

# ---------- Add New Admin ----------
st.subheader("Add New Admin")
new_username = st.text_input("Username", key="add_username")
new_password = st.text_input("Password", type="password", key="add_password")

if st.button("Add Admin"):
    if not new_username or not new_password:
        st.warning("Please enter both username and password!")
    else:
        success = add_admin_db(new_username, new_password)
        if success:
            st.success(f"Admin '{new_username}' added successfully ✅")
        else:
            st.error("Username already exists!")

# ---------- Delete Admin ----------
st.subheader("Delete Admin")
admins = get_all_admins_db()
if not admins:
    st.info("No admins found.")
else:
    admin_to_delete = st.selectbox("Select Admin to Delete", admins)
    if st.button("Delete Admin"):
        delete_admin_db(admin_to_delete)
        st.success(f"Admin '{admin_to_delete}' deleted successfully ✅")
