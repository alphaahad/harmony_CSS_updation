import streamlit as st
from project_utils import *

# --- Page Config ---
st.set_page_config(page_title="Harmony", layout="wide")
st.title("Project Harmony")

# --- Global Dark Theme CSS ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap" rel="stylesheet">
<style>
    html, body, .stApp {
        font-family: 'Quicksand', sans-serif;
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6, label, p, div, span {
        color: #ffffff !important;
    }

    /* Input Fields */
    section[data-testid="stTextInput"] input,
    section[data-testid="stTextArea"] textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 8px;
        padding: 10px;
        font-weight: 500;
    }

    /* Global Button Styling — Targets ALL buttons */
    button {
        background-color: #222222 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6em 1.2em !important;
        transition: all 0.2s ease-in-out;
    }

    button:hover {
        background-color: #444444 !important;
        transform: scale(1.03);
    }

    /* Floating Buttons */
    .stButton > button.fab {
        position: fixed;
        bottom: 20px;
        background-color: #222222 !important;
        color: #ffffff !important;
        border: none;
        padding: 12px 16px;
        font-size: 22px;
        border-radius: 50%;
        box-shadow: 2px 2px 10px rgba(255,255,255,0.2);
        z-index: 9999;
    }

    div[data-testid="column"]:nth-of-type(1) button.fab {
        right: 90px;
    }

    div[data-testid="column"]:nth-of-type(2) button.fab {
        right: 30px;
    }

    /* Note Card */
    .note-card {
        background-color: #1c1c1c;
        color: #ffffff !important;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 2px 2px 10px rgba(255,255,255,0.1);
        font-size: 15px;
        line-height: 1.5;
        transition: all 0.2s ease;
    }

    .note-card:hover {
        transform: scale(1.02);
        box-shadow: 3px 3px 12px rgba(255,255,255,0.15);
    }

    /* Alerts */
    .stAlert {
        background-color: #222222 !important;
        border-left: 5px solid #ffffff;
        color: #ffffff !important;
    }

    /* Download Button */
    .stDownloadButton > button {
        background-color: #222222 !important;
        color: #ffffff !important;
        border-radius: 10px;
    }

    .stDownloadButton > button:hover {
        background-color: #444444 !important;
    }

    /* Logout Button (fixed shape, no wrapping) */
.logout-button {
    position: fixed;
    top: 45px;
    right: 25px;
    z-index: 1000;
    background-color: #f44336 !important;
    color: white !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    white-space: nowrap !important;
    min-width: 80px !important;
    text-align: center !important;
}

</style>
""", unsafe_allow_html=True)

# --- Session State ---
for key, val in {"view_note": None, "show_form": False, "show_analysis": False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Login Screen ---
if "email" not in st.session_state:
    login_screen()
    st.stop()

# --- Logout Button ---
space, col1 = st.columns([15, 1])
with col1:
    st.markdown("""
    <style>
    div.stButton > button.logout-button {
        background-color: #f44336 !important;
        color: white !important;
        padding: 10px 20px !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        white-space: nowrap !important;
        min-width: 90px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("Logout", key="logout", help="Log out of Harmony"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# --- Floating Buttons ---
space, col2, col1 = st.columns([25, 1, 1])
with col1:
    if st.button("➕", key="float-add"):
        st.session_state.show_form = True
        st.session_state.view_note = None
        st.session_state.show_analysis = False
with col2:
    if st.button("📊", key="float_button"):
        st.session_state.show_form = False
        st.session_state.view_note = None
        st.session_state.show_analysis = True

# --- View Note ---
if st.session_state.view_note:
    try:
        df = get_notes_from_supabase()
        note_id = st.session_state.view_note
        result = df[df["id"] == int(note_id)]

        if not result.empty:
            note = result.iloc[0]
            title = note["title"]
            text = note["body"]
            prediction = note["prediction_message"]

            st.subheader(title)
            st.markdown(prediction)

            with st.form("edit_note_form"):
                new_title = st.text_input("Edit Title", value=title)
                new_text = st.text_area("Edit Note", value=text, height=300)

                col1, _, col2, _, col3, _, col4 = st.columns([1, 2, 1, 2, 1, 2, 1])
                save = col1.form_submit_button("Save Changes")
                update = col2.form_submit_button("Update Prediction")
                delete = col3.form_submit_button("Delete Note")
                back = col4.form_submit_button("Back to All Notes")

            if save:
                p = predict_both(new_text)
                delete_note_from_supabase(int(note_id))
                save_note_to_supabase(new_title, new_text, p[0], p[1], p[2])
                st.session_state.view_note = None
                st.rerun()
            elif update:
                p = predict_both(new_text)
                st.info(f"**Updated Prediction:** {p[2]}")
            elif delete:
                delete_note_from_supabase(int(note_id))
                st.session_state.view_note = None
                st.rerun()
            elif back:
                st.session_state.view_note = None
                st.rerun()
        else:
            st.error("Note not found.")
            st.session_state.view_note = None
    except Exception as e:
        st.error(f"Failed to load note: {e}")
        st.session_state.view_note = None

# --- Analysis View ---
elif st.session_state.show_analysis:
    try:
        df = get_notes_from_supabase()
        if df.empty:
            st.error("No notes found.")
        else:
            with st.form("your_analysis"):
                st.subheader("Choose which analysis you need to see")
                selected = st.selectbox("Choose an option:", ["Depression", "Schizophrenia"])

                col1, _, col2 = st.columns([1, 8, 1])
                submit = col1.form_submit_button("Show Analysis")
                back = col2.form_submit_button("Back to Notes")

                if back:
                    st.session_state.show_analysis = False
                    st.rerun()
                if submit:
                    if selected == "Depression":
                        show_analysis_depression()
                    else:
                        show_analysis_schizo()
    except Exception as e:
        st.error(f"Failed to fetch analysis data: {e}")

# --- New Note Form ---
elif st.session_state.show_form:
    with st.form("new_note"):
        st.subheader("Add a New Note")
        title = st.text_input("Title")
        body = st.text_area("Body", height=200)

        if "pending_prediction" not in st.session_state:
            st.session_state.pending_prediction = None

        if st.session_state.pending_prediction:
            st.info(f"Prediction: {st.session_state.pending_prediction}")

        col1, _, col2, _, col3 = st.columns([2, 5, 1, 5, 1])
        pred = col1.form_submit_button("Get Prediction")
        save = col2.form_submit_button("Save")
        cancel = col3.form_submit_button("Cancel")

    if pred:
        if body.strip() == "":
            st.warning("Note body is empty.")
        else:
            st.session_state.pending_prediction = predict_both(body)[2]
            st.rerun()
    elif save:
        if title.strip() == "":
            st.warning("Please enter a title.")
        else:
            p = predict_both(body)
            save_note_to_supabase(title, body, p[0], p[1], p[2])
            st.session_state.pending_prediction = None
            st.session_state.show_form = False
            st.rerun()
    elif cancel:
        st.session_state.pending_prediction = None
        st.session_state.show_form = False
        st.rerun()

# --- Notes Grid ---
else:
    notes = get_notes_from_supabase()
    if notes.empty:
        st.info("No notes saved yet!")
    else:
        st.subheader("Saved Notes")
        num_cols = 5
        rows = [notes[i:i + num_cols] for i in range(0, len(notes), num_cols)]

        for row in rows:
            cols = st.columns(num_cols, gap="small")
            for idx, (note_series, col) in enumerate(zip(row.iterrows(), cols)):
                _, note = note_series
                title = note["title"]
                preview_text = preview(note["body"])

                with col:
                    st.markdown(f"""
                    <div class="note-card">
                        <strong>{title}</strong><br><br>
                        {preview_text}
                    </div>
                    """, unsafe_allow_html=True)
                    # This will now inherit CSS styling from above
                    if st.button("Open", key=f"open_btn_{note['id']}_{idx}"):
                        st.session_state.view_note = note["id"]
                        st.rerun()
