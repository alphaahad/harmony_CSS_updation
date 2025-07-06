import streamlit as st
from project_utils import *

# --- Page Setup ---
st.set_page_config(page_title="Harmony", layout="wide")

# --- Enlarge Buttons ---
st.markdown("""
    <style>
    button[kind="secondary"] {
        font-size: 20px !important;
        padding: 12px 20px !important;
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

# --- Session Init ---
for key, val in {"view_note": None, "show_form": False, "show_analysis": False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Login Page ---
if "email" not in st.session_state:
    login_screen()
    st.stop()

# --- Top Row: Buttons Left, Logout Right ---
button_col1, button_col2, spacer, logout_col = st.columns([0.06, 0.06, 0.76, 0.12])

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

with logout_col:
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- View Specific Note ---
if st.session_state.view_note:
    df = get_notes_from_supabase()
    note_id = st.session_state.view_note
    note = df[df["id"] == int(note_id)].iloc[0]

    st.subheader(f"Editing: {note['title']}")
    st.write(note["prediction_message"])

    # Inject custom CSS for button spacing
    st.markdown("""
    <style>
    .stButton>button {
        height: 48px;
        font-size: 16px;
        border-radius: 8px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("edit_note_form"):
        new_title = st.text_input("Title", value=note["title"])
        new_body = st.text_area("Body", value=note["body"], height=250)

        # Arrange buttons in a single row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            save_btn = st.form_submit_button("💾 Save")
        with col2:
            update_btn = st.form_submit_button("🔁 Update Prediction")
        with col3:
            delete_btn = st.form_submit_button("🗑️ Delete Note")
        with col4:
            back_btn = st.form_submit_button("🔙 Back")

    if save_btn:
        if new_title.strip() and new_body.strip():
            p = predict_both(new_body)
            delete_note_from_supabase(int(note_id))
            save_note_to_supabase(new_title, new_body, p[0], p[1], p[2])
            st.success("Note updated successfully.")
            st.session_state.view_note = None
            st.rerun()
        else:
            st.warning("Title and body cannot be empty.")

    elif update_btn:
        if new_body.strip():
            _, _, new_msg = predict_both(new_body)
            st.info(f"Updated Prediction: {new_msg}")
        else:
            st.warning("Cannot update prediction on empty note.")

    elif delete_btn:
        delete_note_from_supabase(int(note_id))
        st.success("Note deleted.")
        st.session_state.view_note = None
        st.rerun()

    elif back_btn:
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
    st.subheader("📝 New Journal Entry" if st.session_state.view_note is None else "✏️ Edit Journal Entry")

    # Pre-fill values if editing
    default_title = ""
    default_body = ""
    default_mood = "😐 Neutral"
    default_help = "No"

    if st.session_state.view_note:
        df = get_notes_from_supabase()
        note_id = st.session_state.view_note
        note = df[df["id"] == int(note_id)].iloc[0]
        default_title = note["title"]
        default_body = note["body"]

    title = st.text_input("Title", value=default_title)
    body = st.text_area("Write your journal entry here:", height=200, value=default_body)


    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Update Prediction"):
            p = predict_both(body)
            st.session_state.prediction = p[0]
            st.session_state.prediction_message = p[1]
            st.success(f"{p[1]} (Confidence: {round(p[2]*100, 2)}%)")

    with col2:
        if st.button("💾 Save Note"):
            if title.strip() and body.strip():
                p = predict_both(body) if "prediction" not in st.session_state else (
                    st.session_state.prediction,
                    st.session_state.prediction_message,
                    0.0
                )
                save_note_to_supabase(title, body, p[0], p[1], p[2])
                st.session_state.show_form = False
                st.session_state.prediction = None
                st.session_state.prediction_message = None
                st.session_state.view_note = None
                st.rerun()
            else:
                st.warning("Title and body cannot be empty.")

    with col3:
        if st.button("🔙 Cancel"):
            st.session_state.show_form = False
            st.session_state.view_note = None
            st.session_state.prediction = None
            st.session_state.prediction_message = None
            st.rerun()


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
                with st.container():
                    st.markdown("#### " + note["title"])
                    st.text_area(
                        label="Preview",
                        value=preview(note["body"]),
                        height=180,
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"note_preview_{note['id']}"
                    )
                    if st.button("Open", key=f"open_note_{note['id']}"):
                        st.session_state.view_note = note["id"]
                        st.rerun()
