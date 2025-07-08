import streamlit as st
from project_utils import *
import time

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

# --- Title ---
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

    # Navigation options
    nav_options = ["Saved Notes", "New Note", "Statistics"]
    selected_option = None

    for option in nav_options:
        btn_key = f"nav_{option.replace(' ', '_')}"
        active_class = "nav-button nav-button-active" if st.session_state.nav_choice == option else "nav-button"
        if st.button(option, key=btn_key):
            selected_option = option
        st.markdown(f"""
            <script>
            var btn = window.parent.document.querySelectorAll('button[data-testid="button-{btn_key}"]')[0];
            if (btn) {{
                btn.className = "{active_class}";
            }}
            </script>
        """, unsafe_allow_html=True)

    if selected_option:
        st.session_state.nav_choice = selected_option
        st.experimental_rerun()

    st.markdown("---")
    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# --- View State from nav_choice ---
if st.session_state.nav_choice == "New Note":
    st.session_state.show_form = True
    st.session_state.view_note = None
    st.session_state.show_analysis = False
elif st.session_state.nav_choice == "Statistics":
    st.session_state.show_form = False
    st.session_state.view_note = None
    st.session_state.show_analysis = True
else:
    if st.session_state.view_note is None:
        st.session_state.show_form = False
        st.session_state.show_analysis = False

# --- View Note ---
if st.session_state.view_note:
    df = get_notes_from_supabase()
    note_id = st.session_state.view_note
    note = df[df["id"] == int(note_id)].iloc[0]

    st.subheader(f"Editing: {note['title']}")

    prediction_msg = note.get("prediction_message", "")
    if isinstance(prediction_msg, str) and prediction_msg.strip() and prediction_msg.strip() != "0.0":
        st.info(prediction_msg)

    new_title = st.text_input("Title (max 100 characters)", value=note["title"][:100], max_chars=100, key="edit_title")
    new_body = st.text_area("Body", value=note["body"], height=250, key="edit_body")

    st.markdown("""
    <style>
        div.stButton > button {
            width: 100% !important;
            height: 3rem;
            font-size: 16px;
            font-weight: 600;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    rerun_flag = False

    with col1:
        if st.button("Update and Save Note"):
            if new_title.strip() and new_body.strip():
                prediction = predict_both(new_body)
                delete_note_from_supabase(int(note_id))
                save_note_to_supabase(
                    title=new_title,
                    body=new_body,
                    pred_depression=prediction[0],
                    pred_schizophrenia=prediction[1],
                    prediction_message=prediction[2]
                )
                st.success("Note updated successfully.")
                time.sleep(2)
                st.session_state.view_note = None
                rerun_flag = True
            else:
                st.warning("Title and body cannot be empty.")

    with col2:
        if st.button("Delete Note"):
            delete_note_from_supabase(int(note_id))
            st.success("Note deleted.")
            st.session_state.view_note = None
            rerun_flag = True

    with col3:
        if st.button("Back"):
            st.session_state.view_note = None
            rerun_flag = True

    if rerun_flag:
        st.experimental_rerun()

    st.stop()

# --- Statistics View ---
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

# --- New Note View ---
elif st.session_state.show_form:
    st.subheader("New Journal Entry")

    title = st.text_input("Title (max 100 characters)", max_chars=100)
    body = st.text_area("Write your journal entry here:", height=200)

    save_flag = False
    if st.button("Predict and Save Note"):
        if title.strip() and body.strip():
            prediction = predict_both(body)
            save_note_to_supabase(
                title=title,
                body=body,
                pred_depression=prediction[0],
                pred_schizophrenia=prediction[1],
                prediction_message=prediction[2]
            )
            st.success(f"{prediction[2]}")
            time.sleep(2)
            st.session_state.show_form = False
            st.session_state.prediction = None
            st.session_state.prediction_message = None
            st.session_state.view_note = None
            st.session_state.nav_choice = "Saved Notes"
            save_flag = True
        else:
            st.warning("Title and body cannot be empty.")

    if save_flag:
        st.experimental_rerun()

    st.stop()

# --- Saved Notes Grid ---
st.subheader("Saved Notes")
df = get_notes_from_supabase()

if df.empty:
    st.info("No notes found.")
else:
    note_to_open = None
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
                    note_to_open = note["id"]

    if note_to_open:
        st.session_state.view_note = note_to_open
        st.experimental_rerun()
