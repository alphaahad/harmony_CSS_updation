import streamlit as st
from project_utils import *

# ====== PAGE CONFIG ======
st.set_page_config(page_title="HARMONY", layout="wide")

# ====== FONT & CSS ======
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap" rel="stylesheet">
<style>
html, body, .stApp {
    font-family: 'Quicksand', sans-serif;
    background-color: #f7f7f9;
    color: #222;
}

/* Logout button */
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
    white-space: nowrap !important;
    min-width: 90px !important;
    text-align: center !important;
}

/* Floating buttons */
.fab-button {
    position: fixed;
    right: 30px;
    width: 55px;
    height: 55px;
    border-radius: 50%;
    font-size: 24px;
    z-index: 999;
    border: none !important;
    font-weight: bold;
    background-color: #0059b3 !important;
    color: white !important;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
}

#float-add {
    bottom: 110px;
}
#float-chart {
    bottom: 40px;
}

/* Note cards */
.note-card {
    border-radius: 12px;
    padding: 15px;
    height: 220px;
    overflow: hidden;
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
</style>
""", unsafe_allow_html=True)

# ====== SESSION INIT ======
for key, val in {"view_note": None, "show_form": False, "show_analysis": False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ====== LOGGED OUT VIEW ======
if "email" not in st.session_state:
    login_screen()
    st.stop()

# ====== LOGOUT BUTTON ======
st.markdown('<button class="logout-button" onclick="window.location.reload();">Logout</button>', unsafe_allow_html=True)

# ====== FLOATING BUTTONS ======
st.markdown("""
<button class="fab-button" id="float-add" onclick="parent.postMessage({type: 'streamlit:rerunScript', rerunScript: 'add'}, '*');">➕</button>
<button class="fab-button" id="float-chart" onclick="parent.postMessage({type: 'streamlit:rerunScript', rerunScript: 'charts'}, '*');">📊</button>
""", unsafe_allow_html=True)

# ====== HACK TO CATCH FLOATING BUTTONS ======
float_trigger = st.experimental_get_query_params()
if "rerunScript" in float_trigger:
    if float_trigger["rerunScript"][0] == "add":
        st.session_state.show_form = True
        st.session_state.view_note = None
        st.session_state.show_analysis = False
    elif float_trigger["rerunScript"][0] == "charts":
        st.session_state.show_form = False
        st.session_state.view_note = None
        st.session_state.show_analysis = True

# ====== VIEW NOTE SECTION ======
if st.session_state.view_note:
    df = get_notes_from_supabase()
    note_id = st.session_state.view_note
    result = df[df["id"] == int(note_id)]
    if not result.empty:
        note = result.iloc[0]
        st.subheader(note["title"])
        st.markdown(note["prediction_message"])
        with st.form("edit_note_form"):
            new_title = st.text_input("Edit Title", value=note["title"])
            new_text = st.text_area("Edit Note", value=note["body"], height=300)
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            save = col1.form_submit_button("Save")
            update = col2.form_submit_button("Update")
            delete = col3.form_submit_button("Delete")
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

# ====== ANALYSIS SECTION ======
elif st.session_state.show_analysis:
    df = get_notes_from_supabase()
    if df.empty:
        st.info("No entries found.")
    else:
        with st.form("analysis_form"):
            st.subheader("Choose Analysis Type")
            selected = st.selectbox("Select:", ["Depression", "Schizophrenia"])
            col1, col2 = st.columns(2)
            show = col1.form_submit_button("Show")
            back = col2.form_submit_button("Back to Notes")
        if back:
            st.session_state.show_analysis = False
            st.rerun()
        if show:
            if selected == "Depression":
                show_analysis_depression()
            else:
                show_analysis_schizo()

# ====== ADD NOTE SECTION ======
elif st.session_state.show_form:
    with st.form("add_note_form"):
        st.subheader("New Note")
        title = st.text_input("Title")
        body = st.text_area("Body", height=200)
        col1, col2, col3 = st.columns(3)
        pred = col1.form_submit_button("Get Prediction")
        save = col2.form_submit_button("Save")
        cancel = col3.form_submit_button("Cancel")

    if pred:
        if not body.strip():
            st.warning("Body is empty.")
        else:
            st.session_state.pending_prediction = predict_both(body)[2]
            st.rerun()
    elif save:
        if not title.strip():
            st.warning("Please provide a title.")
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

# ====== NOTES GRID SECTION ======
else:
    notes = get_notes_from_supabase()
    if notes.empty:
        st.info("No notes yet.")
    else:
        st.subheader("Saved Notes")
        num_cols = 5
        rows = [notes[i:i + num_cols] for i in range(0, len(notes), num_cols)]
        colors = ["#e3d7ff", "#fff3c1", "#d9f5d9", "#ffd4d4", "#e0f7fa"]
        for row in rows:
            cols = st.columns(num_cols)
            for idx, (i, note) in enumerate(row.iterrows()):
                with cols[idx]:
                    bg_color = colors[idx % len(colors)]
                    st.markdown(f"""
                    <div class="note-card" style="background-color:{bg_color};">
                        <strong>{note['title']}</strong><br><br>
                        <div class='note-preview'>{preview(note['body'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Open", key=f"open_btn_{note['id']}"):
                        st.session_state.view_note = note["id"]
                        st.rerun()
