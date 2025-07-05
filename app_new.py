import streamlit as st
from project_utils import *
import random

# ==== Page Config ====
st.set_page_config(page_title="Harmony", layout="wide")
st.title("Project Harmony")

# ==== Font + Light Theme CSS ====
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap" rel="stylesheet">
<style>
html, body, .stApp {
    font-family: 'Quicksand', sans-serif;
    background-color: #f5f7fa !important;
    color: #2b2b2b !important;
}
h1, h2, h3, h4, h5, h6, label, p, div, span {
    color: #2b2b2b !important;
}

/* Floating buttons stacked */
.fab-stack {
    position: fixed;
    bottom: 30px;
    right: 30px;
    display: flex;
    flex-direction: column;
    gap: 15px;
    z-index: 9999;
}
.fab-btn {
    background-color: #1976d2 !important;
    color: white !important;
    border: none;
    padding: 14px;
    border-radius: 50%;
    font-size: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    transition: all 0.2s ease;
}
.fab-btn:hover {
    background-color: #1565c0 !important;
    transform: scale(1.05);
}

/* Logout Button */
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

/* Note cards with equal height and variable pastel backgrounds */
.note-card {
    background-color: #e3f2fd;
    border-radius: 12px;
    padding: 15px;
    height: 220px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    transition: all 0.2s ease-in-out;
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
</style>
""", unsafe_allow_html=True)

# ==== Logout Button (visible only after login) ====
if "email" in st.session_state:
    st.markdown("""
    <script>
    const buttons = window.parent.document.querySelectorAll('button');
    for (let btn of buttons) {
        if (btn.innerText === "Logout") {
            btn.classList.add("logout-button");
        }
    }
    </script>
    """, unsafe_allow_html=True)
    if st.button("Logout", key="logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==== Session State Defaults ====
for key, val in {"view_note": None, "show_form": False, "show_analysis": False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==== Login Screen ====
if "email" not in st.session_state:
    login_screen()
    st.stop()

# ==== Floating Action Buttons ====
st.markdown("""
<div class="fab-stack">
    <form action="" method="POST">
        <button class="fab-btn" name="float_add" type="submit">➕</button><br>
        <button class="fab-btn" name="float_chart" type="submit">📊</button>
    </form>
</div>
""", unsafe_allow_html=True)

if st.experimental_get_query_params().get("float_add"):
    st.session_state.show_form = True
    st.session_state.view_note = None
    st.session_state.show_analysis = False
elif st.experimental_get_query_params().get("float_chart"):
    st.session_state.show_form = False
    st.session_state.view_note = None
    st.session_state.show_analysis = True

# ==== Render Screens ====

# View Specific Note
if st.session_state.view_note:
    view_note_screen()

# Show Analysis
elif st.session_state.show_analysis:
    analysis_screen()

# Add New Note
elif st.session_state.show_form:
    new_note_screen()

# Show Notes Grid
else:
    notes = get_notes_from_supabase()
    if notes.empty:
        st.info("No notes saved yet.")
    else:
        st.subheader("Saved Notes")
        num_cols = 4
        rows = [notes[i:i + num_cols] for i in range(0, len(notes), num_cols)]
        pastel_colors = ["#ffe0e0", "#e0f7fa", "#fff9c4", "#f1f8e9", "#ede7f6", "#e8f5e9", "#fff3e0"]

        for row in rows:
            cols = st.columns(num_cols)
            for idx, (note_series, col) in enumerate(zip(row.iterrows(), cols)):
                _, note = note_series
                bg_color = random.choice(pastel_colors)
                preview_text = preview(note["body"])

                with col:
                    st.markdown(f"""
                    <div class="note-card" style="background-color:{bg_color};">
                        <strong>{note['title']}</strong><br><br>
                        <div class="note-preview">{preview_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Open", key=f"open_btn_{note['id']}_{idx}"):
                        st.session_state.view_note = note["id"]
                        st.rerun()
