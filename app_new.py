import streamlit as st
from project_utils import *

# --- Page Setup ---
st.set_page_config(page_title="Harmony", layout="wide")

st.markdown("""
    <style>
    button[kind="secondary"] {
        font-size: 20px !important;
        padding: 12px 18px !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Centered Heading Using HTML ---
st.markdown("""
    <h1 style='text-align: center; font-weight: 600; margin-top: 20px;'>
                     PROJECT HARMONY
    </h1>
""", unsafe_allow_html=True)

# --- Logout Button (Top-Right, only after login) ---
if "email" in st.session_state:
    top_col1, top_col2 = st.columns([10, 1])
    with top_col2:
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# --- Session Init ---
for key, val in {"view_note": None, "show_form": False, "show_analysis": False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Login Page ---
if "email" not in st.session_state:
    login_screen()
    st.stop()

# --- Top-Left Action Buttons (side by side, enlarged) ---
button_col1, button_col2, _ = st.columns([0.06, 0.06, 0.88])

with button_col1:
    if st.button("➕", key="add_note", help="Add New Note"):
        st.session_state.show_form = True
        st.session_state.view_note = None
        st.session_state.show_analysis = False

with button_col2:
    if st.button("📊", key="view_stats", help="View Statistics"):
        st.session_state.show_form = False
        st.session_state.view_note = None
        st.session_state.show_analysis = True

# --- View Specific Note ---
if st.session_state.view_note:
    df = get_notes_from_supabase()
    note_id = st.session_state.view_note
    note = df[df["id"] == int(note_id)].iloc[0]
    st.subheader(note["title"])
    st.write(note["prediction_message"])
    st.text_area("Note", value=note["body"], height=250, disabled=True)
    if st.button("Back"):
        st.session_state.view_note = None
        st.rerun()

# --- View Analysis ---
elif st.session_state.show_analysis:
    with st.form("choose_analysis"):
        option = st.selectbox("Which analysis?", ["Depression", "Schizophrenia"])
        submitted = st.form_submit_button("Show")
    if submitted:
        if option == "Depression":
            show_analysis_depression()
        else:
            show_analysis_schizo()
    if st.button("Back to Notes"):
        st.session_state.show_analysis = False
        st.rerun()

# --- Add New Note ---
elif st.session_state.show_form:
    with st.form("new_note_form"):
        title = st.text_input("Title")
        body = st.text_area("Body", height=200)
        submitted = st.form_submit_button("Save")
    if submitted:
        if title.strip() and body.strip():
            p = predict_both(body)
            save_note_to_supabase(title, body, p[0], p[1], p[2])
            st.session_state.show_form = False
            st.rerun()
        else:
            st.warning("Title and body cannot be empty.")

# --- Show Notes Grid ---
else:
    st.subheader("Saved Notes")
    df = get_notes_from_supabase()
    if df.empty:
        st.info("No notes found.")
    else:
        cols = st.columns(3)
        for idx, (_, note) in enumerate(df.iterrows()):
            with cols[idx % 3]:
                st.markdown("#### " + note["title"])
                st.text_area(
                    "Preview",
                    value=preview(note["body"]),
                    height=140,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"note_preview_{note['id']}"
                )
                if st.button("Open", key=f"open_note_{note['id']}"):
                    st.session_state.view_note = note["id"]
                    st.rerun()
