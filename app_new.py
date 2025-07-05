import streamlit as st
import random
from project_utils import *

# --- Page Config ---
st.set_page_config(page_title="Harmony", layout="wide")

# --- Light Theme and Fonts ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap" rel="stylesheet">
<style>
    html, body, .stApp {
        font-family: 'Quicksand', sans-serif;
        background-color: #f7f7f9;
        color: #222;
    }

    h1, h2, h3, h4, h5, h6, label, p, div, span {
        color: #222 !important;
    }

    .note-card {
        border-radius: 12px;
        padding: 15px;
        height: 220px;
        overflow: hidden;
        position: relative;
        box-shadow: 0 1px 6px rgba(0,0,0,0.1);
        transition: all 0.25s ease-in-out;
    }

    .note-card:hover {
        transform: translateY(-2px);
    }

    .note-preview {
        white-space: pre-wrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-height: 120px;
    }

    .logout-button {
        position: fixed;
        top: 20px;
        right: 25px;
        z-index: 1000;
        background-color: #e53935 !important;
        color: white !important;
        padding: 10px 20px !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    .fab {
        position: fixed;
        right: 25px;
        padding: 12px 16px;
        font-size: 24px;
        border-radius: 50%;
        background-color: #0059b3 !important;
        color: white !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
        z-index: 9999;
    }

    #fab-add {
        bottom: 100px;
    }

    #fab-chart {
        bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- Session Init ---
for key in ["view_note", "show_form", "show_analysis"]:
    if key not in st.session_state:
        st.session_state[key] = False

# --- Authentication ---
if "email" not in st.session_state:
    login_screen()
    st.stop()

# --- Logout ---
if st.button("Logout", key="logout", help="Sign out"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.markdown("""
<script>
const logoutBtn = window.parent.document.querySelector('button[title="Sign out"]');
if (logoutBtn) logoutBtn.classList.add("logout-button");
</script>
""", unsafe_allow_html=True)

# --- Floating Buttons (with working logic) ---
st.markdown("<br><br>", unsafe_allow_html=True)
fab1, spacer, fab2 = st.columns([0.07, 0.01, 0.07])

with fab1:
    if st.button("➕", key="float_add"):
        st.session_state.show_form = True
        st.session_state.view_note = None
        st.session_state.show_analysis = False

with fab2:
    if st.button("📊", key="float_chart"):
        st.session_state.show_form = False
        st.session_state.view_note = None
        st.session_state.show_analysis = True

# --- Floating Button Styles ---
st.markdown("""
<style>
button[kind="secondary"] {
    border-radius: 50% !important;
    font-size: 22px !important;
    width: 55px !important;
    height: 55px !important;
    padding: 0 !important;
    margin-bottom: 15px !important;
    background-color: #0059b3 !important;
    color: white !important;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2) !important;
}
</style>
""", unsafe_allow_html=True)


# --- State Handling ---
if st.session_state.show_form:
    show_add_note_form()
elif st.session_state.show_analysis:
    show_analysis()
elif st.session_state.view_note:
    show_note_detail()
else:
    # --- Notes Grid ---
    df = get_notes_from_supabase()
    if df.empty:
        st.info("No notes saved yet!")
    else:
        st.subheader("Saved Notes")
        cols_per_row = 5
        rows = [df[i:i + cols_per_row] for i in range(0, len(df), cols_per_row)]
        pastel_colors = ['#fde2e2', '#fff1ba', '#d0f4de', '#e0c3fc', '#c1f0f6']

        for row in rows:
            cols = st.columns(cols_per_row)
            for i, (idx, note) in enumerate(row.iterrows()):
                with cols[i]:
                    color = random.choice(pastel_colors)
                    st.markdown(f"""
                    <div class="note-card" style="background-color: {color}">
                        <strong>{note["title"]}</strong>
                        <div class="note-preview">{preview(note["body"])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Open", key=f"open_btn_{note['id']}_{i}"):
                        st.session_state.view_note = note["id"]
                        st.rerun()
