import streamlit as st
from project_utils import *

# --- Page Config ---
st.set_page_config(page_title="Harmony", layout="wide")

# --- Session Initialization ---
for key, val in {"view_note": None, "show_form": False, "show_analysis": False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Login ---
if "email" not in st.session_state:
    login_screen()
    st.stop()

# --- Logout Button ---
if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.title("🧠 Project Harmony")

# --- Floating Buttons ---
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ New Note"):
        st.session_state.show_form = True
        st.session_state.view_note = None
        st.session_state.show_analysis = False
with col2:
    if st.button("📊 View Charts"):
        st.session_state.show_form = False
        st.session_state.view_note = None
        st.session_state.show_analysis = True

# --- View Note ---
if st.session_state.view_note:
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
            col1, col2, col3, col4 = st.columns(4)
            save = col1.form_submit_button("Save Changes")
            update = col2.form_submit_button("Update Prediction")
            delete = col3.form_submit_button("Delete Note")
            back = col4.form_submit_button("Back")

        if save:
            p = predict_both(new_text)
            delete_note_from_supabase(int(note_id))
            save_note_to_supabase(new_title, new_text, p[0], p[1], p[2])
            st.session_state.view_note = None
            st.rerun()
        elif update:
            p = predict_both(new_text)
            st.info(f"Updated Prediction: {p[2]}")
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

# --- Analysis View ---
elif st.session_state.show_analysis:
    df = get_notes_from_supabase()
    if df.empty:
        st.warning("No notes available.")
    else:
        with st.form("choose_analysis"):
            st.subheader("Choose analysis type:")
            selected = st.selectbox("Select", ["Depression", "Schizophrenia"])
            col1, col2 = st.columns([1, 1])
            submit = col1.form_submit_button("Show")
            back = col2.form_submit_button("Back")

        if back:
            st.session_state.show_analysis = False
            st.rerun()
        if submit:
            if selected == "Depression":
                show_analysis_depression()
            else:
                show_analysis_schizo()

# --- New Note ---
elif st.session_state.show_form:
    with st.form("new_note"):
        st.subheader("Add a New Note")
        title = st.text_input("Title")
        body = st.text_area("Body", height=200)

        if "pending_prediction" not in st.session_state:
            st.session_state.pending_prediction = None

        if st.session_state.pending_prediction:
            st.info(f"Prediction: {st.session_state.pending_prediction}")

        col1, col2, col3 = st.columns(3)
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
        num_cols = 3
        rows = [notes[i:i + num_cols] for i in range(0, len(notes), num_cols)]

        for row in rows:
            cols = st.columns(num_cols)
            for idx, (note_series, col) in enumerate(zip(row.iterrows(), cols)):
                _, note = note_series
                title = note["title"]
                preview_text = preview(note["body"])

                with col:
                    st.markdown(f"#### {title}")
                    st.markdown(preview_text)
                    if st.button("Open", key=f"open_btn_{note['id']}_{idx}"):
                        st.session_state.view_note = note["id"]
                        st.rerun()
