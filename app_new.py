import streamlit as st
from project_utils import *

# --- Page config ---
st.set_page_config(page_title="Harmony", layout="wide")
st.title("Project Harmony")

# --- CSS Styling ---
# --- CSS Styling ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap" rel="stylesheet">
<style>
    html, body, .stApp {
        font-family: 'Quicksand', sans-serif;
        background-color: #165239 !important;
        color: #165239 !important;
    }

    h1, h2, h3, h4, h5, h6, label, p, div, span, .stMarkdown {
        color: #ffffff !important;
    }

    /* Inputs and Text Areas */
    section[data-testid="stTextInput"] input,
    section[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #165239 !important;
        border: 1px solid #c4e8c3 !important;
        border-radius: 8px;
        padding: 10px;
        font-weight: 500;
    }

    /* All primary buttons */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #165239 !important;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background-color: #f2fdf2 !important;
        transform: scale(1.03);
        color: #165239 !important;
    }

    /* Floating Buttons */
    .stButton > button.fab {
        position: fixed;
        bottom: 20px;
        background-color: #ffffff !important;
        color: #165239 !important;
        border: none;
        padding: 12px 16px;
        font-size: 22px;
        border-radius: 50%;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        z-index: 9999;
    }

    div[data-testid="column"]:nth-of-type(1) button.fab {
        right: 90px;
    }

    div[data-testid="column"]:nth-of-type(2) button.fab {
        right: 30px;
    }

    /* Note Cards */
    .note-card {
        background-color: #ffffff;
        color: #165239 !important;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        font-size: 15px;
        line-height: 1.5;
        transition: all 0.2s ease;
    }

    .note-card:hover {
        transform: scale(1.02);
        box-shadow: 3px 3px 12px rgba(0,0,0,0.25);
    }

    .stDataFrame, .stTable {
        background-color: #ffffff !important;
        color: #165239 !important;
    }

    .stAlert {
        background-color: #ffffff !important;
        border-left: 5px solid #165239;
        color: #165239 !important;
    }

    .stDownloadButton > button {
        background-color: #ffffff !important;
        color: #165239 !important;
        border-radius: 10px;
    }

    .stDownloadButton > button:hover {
        background-color: #f1fff1 !important;
    }

    /* Logout Button */
    .stButton > button.logout-button {
        position: fixed;
        top: 45px;
        right: 25px;
        z-index: 1000;
        background-color: #f44336 !important;
        color: white !important;
        padding: 10px 15px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
for key, val in {"view_note": None, "show_form": False, "show_analysis": False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Login Logic ---
if "email" not in st.session_state:
    login_screen()
    st.stop()

# --- Logout Button ---
space, col1 = st.columns([15,1])
with col1:
    if st.button("Logout", key="logout", help="Log out of Harmony"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Floating Add & Chart Buttons ---
space, col2, col1 = st.columns([25,1,1])
with col1:
    if st.button("➕", key="float-add"):
        st.session_state.show_form = True
        st.session_state.view_note = None
        st.session_state.show_analysis = False
with col2:
    if st.button("📊", key = "float_button"):
        st.session_state.show_form = False
        st.session_state.view_note = None
        st.session_state.show_analysis = True

# --- Note Viewer ---
if st.session_state.view_note:
    try:
        df = get_notes_from_supabase()
        note_id = st.session_state.view_note
        result = df[df["id"] == int(note_id)]

        if not result.empty:
            note = result.iloc[0]
            note_title = note["title"]
            note_text = note["body"]
            prediction_message = note["prediction_message"]

            st.subheader(note_title)
            st.markdown(prediction_message)

            with st.form("edit_note_form"):
                new_title = st.text_input("Edit Title", value=note_title)
                new_text = st.text_area("Edit Note", value=note_text, height=300)

                col1, spacer, col2, spacer, col3, spacer, col4 = st.columns([1, 2, 1, 2, 1, 2, 1])
                save_button = col1.form_submit_button("Save Changes")
                update_pred_button = col2.form_submit_button("Update Prediction")
                delete_button = col3.form_submit_button("Delete Note")
                back_button = col4.form_submit_button("Back to All Notes")

            if save_button:
                prediction = predict_both(new_text)
                delete_note_from_supabase(int(note_id))
                save_note_to_supabase(new_title, new_text, prediction[0], prediction[1], prediction[2])
                st.session_state.view_note = None
                st.rerun()
            elif back_button:
                st.session_state.view_note = None
                st.rerun()
            elif update_pred_button:
                new_prediction = predict_both(new_text)
                st.info(f"**Updated Prediction:** {new_prediction[2]}")
            elif delete_button:
                delete_note_from_supabase(int(note_id))
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
                options = ["Depression", "Schizophrenia"]
                selected = st.selectbox("Choose an option:", options)

                col1, spacer, col2 = st.columns([1, 8, 1])
                submit_analysis = col1.form_submit_button("Show Analysis")
                back_button = col2.form_submit_button("Back to Notes")

                if back_button:
                    st.session_state.view_note = None
                    st.session_state.show_analysis = False
                    st.rerun()

                if submit_analysis:
                    if selected == "Depression":
                        show_analysis_depression()
                    elif selected == "Schizophrenia":
                        show_analysis_schizo()

    except Exception as e:
        st.error(f"Failed to fetch analysis data: {e}")        

# --- Note Form ---
elif st.session_state.show_form:
    with st.form("new_note"):
        st.subheader("Add a New Note")
        title = st.text_input("Title")
        body = st.text_area("Body", height=200)

        if "pending_prediction" not in st.session_state:
            st.session_state.pending_prediction = None

        if st.session_state.pending_prediction:
            st.info(f"Prediction: {st.session_state.pending_prediction}")

        col1, spacer, col2, spacer, col3 = st.columns([2, 5, 1, 5, 1])
        get_pred = col1.form_submit_button("Get Prediction")
        save = col2.form_submit_button("Save")
        cancel = col3.form_submit_button("Cancel")

    if get_pred:
        if body.strip() == "":
            st.warning("Note body is empty.")
        else:
            st.session_state.pending_prediction = predict_both(body)[2]
            st.rerun()

    elif save:
        if title.strip() == "":
            st.warning("Please enter a title.")
        else:
            prediction = predict_both(body)
            save_note_to_supabase(
                title=title,
                body=body,
                pred_depression=prediction[0],
                pred_schizophrenia=prediction[1],
                prediction_message=prediction[2]
            )
            st.session_state.pending_prediction = None
            st.session_state.show_form = False
            st.rerun()

    elif cancel:
        st.session_state.pending_prediction = None
        st.session_state.show_form = False
        st.rerun()

# --- Saved Notes Display ---
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
                display_title = note["title"]
                preview_text = preview(note["body"])

                with col:
                    st.markdown(f"""
                    <div class=\"note-card\">
                        <strong>{display_title}</strong><br><br>
                        {preview_text}
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Open", key=f"open_btn_{note['id']}_{idx}", help="Click to open note"):
                        st.session_state.view_note = note["id"]
                        st.rerun()
