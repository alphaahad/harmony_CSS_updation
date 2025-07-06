import streamlit as st
from project_utils import *

# --- Page Setup ---
st.set_page_config(page_title="Harmony", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    button[kind="secondary"] {
        font-size: 20px !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
    }
    .stButton>button {
        height: 48px;
        font-size: 16px;
        border-radius: 8px;
        width: 100%;
    }
    h1 {
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: 600;
    }
    .nav-button {
        display: block;
        width: 100%;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        background-color: #f0f2f6;
        border: none;
        border-radius: 8px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        color: #333;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .nav-button:hover {
        background-color: #dbe4f0;
    }
    .nav-button-active {
        background-color: #4c83ff;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ Always-visible heading
st.markdown("<h1>PROJECT HARMONY</h1>", unsafe_allow_html=True)

# --- Session Init ---
defaults = {
    "view_note": None,
    "show_form": False,
    "show_analysis": False,
    "nav_choice": "Saved Notes"
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Login ---
if "email" not in st.session_state:
    login_screen()
    st.stop()

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("## Navigation")

    nav_options = ["Saved Notes", "New Note", "Statistics"]
    button_styles = """
        <style>
        .custom-nav-button {
            width: 100%;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        .custom-nav-button.active {
            background-color: #4c83ff !important;
            color: white !important;
        }
        .custom-nav-button.inactive {
            background-color: #f0f2f6 !important;
            color: #333 !important;
        }
        .custom-nav-button:hover {
            background-color: #dbe4f0 !important;
        }
        </style>
    """
    st.markdown(button_styles, unsafe_allow_html=True)

    for option in nav_options:
        is_active = st.session_state.nav_choice == option
        button_key = f"nav_button_{option.replace(' ', '_')}"
        button_label = f"<button class='custom-nav-button {'active' if is_active else 'inactive'}'>{option}</button>"
        if st.markdown(button_label, unsafe_allow_html=True):
            pass  # Dummy label, style only
        if st.button(" ", key=button_key):
            st.session_state.nav_choice = option
            st.rerun()

    st.markdown("---")
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# --- Set View State from nav_choice ---
if st.session_state.nav_choice == "New Note":
    st.session_state.show_form = True
    st.session_state.view_note = None
    st.session_state.show_analysis = False
elif st.session_state.nav_choice == "Statistics":
    st.session_state.show_form = False
    st.session_state.view_note = None
    st.session_state.show_analysis = True
else:  # Saved Notes
    if st.session_state.view_note is None:
        st.session_state.show_form = False
        st.session_state.show_analysis = False

# --- View Note ---
if st.session_state.view_note:
    df = get_notes_from_supabase()
    note_id = st.session_state.view_note
    note = df[df["id"] == int(note_id)].iloc[0]

    st.subheader(f"Editing: {note['title']}")

    # ✅ Filter out junk messages like "0.0"
    prediction_msg = note.get("prediction_message", "")
    if isinstance(prediction_msg, str) and prediction_msg.strip() and prediction_msg.strip() != "0.0":
        st.info(prediction_msg)

    new_title = st.text_input("Title (max 100 characters)", value=note["title"][:100], max_chars=100, key="edit_title")
    new_body = st.text_area("Body", value=note["body"], height=250, key="edit_body")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Save"):
            if new_title.strip() and new_body.strip():
                p = predict_both(new_body)
                delete_note_from_supabase(int(note_id))
                save_note_to_supabase(new_title, new_body, p[0], p[1], p[2])
                st.success("Note updated successfully.")
                st.session_state.view_note = None
                st.rerun()
            else:
                st.warning("Title and body cannot be empty.")
    with col2:
        if st.button("Update Prediction"):
            if new_body.strip():
                _, _, new_msg = predict_both(new_body)
                st.info(f"Updated Prediction: {new_msg}")
            else:
                st.warning("Cannot update prediction on empty note.")
    with col3:
        if st.button("Delete Note"):
            delete_note_from_supabase(int(note_id))
            st.success("Note deleted.")
            st.session_state.view_note = None
            st.rerun()
    with col4:
        if st.button("Back"):
            st.session_state.view_note = None
            st.rerun()

    st.stop()

#---view analysis---
elif st.session_state.show_analysis:
    st.subheader("Statistics Dashboard")
    with st.form("choose_analysis"):
        option = st.selectbox("Which analysis?", ["Depression", "Schizophrenia"])
        submitted = st.form_submit_button("Show")

    if submitted:
        if option == "Depression":
            show_analysis_depression()
        else:
            show_analysis_schizo()

    st.stop()

#--- add new note---
elif st.session_state.show_form:
    st.subheader("New Journal Entry")

    title = st.text_input("Title (max 100 characters)", max_chars=100)
    body = st.text_area("Write your journal entry here:", height=200)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update Prediction"):
            p = predict_both(body)
            st.session_state.prediction = p[0]
            st.session_state.prediction_message = p[1]
            st.success(f"{p[2]}")
    with col2:
        if st.button("Save Note"):
            if title.strip() and body.strip():
                if "prediction" in st.session_state and "prediction_message" in st.session_state:
                    p = (
                        st.session_state.prediction,
                        st.session_state.prediction_message,
                        st.session_state.prediction_message
                    )
                else:
                    p = predict_both(body)

                save_note_to_supabase(title, body, p[0], p[1], p[2])
                st.session_state.show_form = False
                st.session_state.prediction = None
                st.session_state.prediction_message = None
                st.session_state.view_note = None
                st.session_state.nav_choice = "Saved Notes"
                st.rerun()
            else:
                st.warning("Title and body cannot be empty.")

    st.stop()

# --- Notes Grid ---
st.subheader("Saved Notes")
df = get_notes_from_supabase()

if df.empty:
    st.info("No notes found.")
else:
    cols = st.columns(4)
    for idx, (_, note) in enumerate(df.iterrows()):
        with cols[idx % 4]:
            with st.container():
                title_short = note["title"][:20] + ("..." if len(note["title"]) > 20 else "")
                st.markdown("#### " + title_short)
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
