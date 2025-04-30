# app.py
import streamlit as st
import threading, webbrowser, time
import sys
# Try to import local recorder; fall back to uploader if unavailable
try:
    from functions.record_audio import start_recording, stop_recording
    RECORD_AVAILABLE = True
except (ImportError, OSError):
    RECORD_AVAILABLE = False
from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx

st.set_page_config(page_title="Psychotherapie‐Antrag Generator", layout="centered")
st.title("📝 Psychotherapie‐Memo aufnehmen und Antrag erstellen")

# --- Session state defaults ---
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "memo_ready" not in st.session_state:
    st.session_state.memo_ready = False

# --- Callbacks to flip state and manage recording ---
def _on_start():
    start_recording("memo.wav")
    st.session_state.is_recording = True
    st.session_state.memo_ready = False

def _on_stop():
    stop_recording()
    st.session_state.is_recording = False
    st.session_state.memo_ready = True

# --- Audio input (either record or upload) ---
slot = st.empty()
if RECORD_AVAILABLE:
    if not st.session_state.is_recording:
        slot.button("🎙️ Start Recording", key="start_btn", on_click=_on_start)
    else:
        slot.button("⏹️ Stop Recording", key="stop_btn", on_click=_on_stop)
else:
    uploaded = slot.file_uploader("🔉 Upload your audio memo", type=["wav","mp3"])
    if uploaded:
        st.session_state.audio_file = uploaded
        st.session_state.memo_ready = True

# --- Once stopped, process the memo ---
if st.session_state.memo_ready:
    # 1) Transcription
    if RECORD_AVAILABLE:
        audio_src = open("memo.wav", "rb")
    else:
        audio_src = st.session_state.audio_file
    transcript = create_transcript(audio_src)
    st.subheader("🎧 Transkript")
    st.text_area("", transcript, height=200)

    # 2) LLM Call
    st.info("Erstelle Psychotherapie‐Antrag…")
    antrag_json = LLMCall(transcript)
    st.subheader("📄 Antrag als JSON")
    st.json(antrag_json)

    # 3) DOCX & Download
    doc_path = "Psychotherapie_Antrag.docx"
    create_docx(antrag_json, doc_path)
    with open(doc_path, "rb") as doc_file:
        st.download_button(
            label="💾 Word-Dokument herunterladen",
            data=doc_file,
            file_name="Psychotherapie_Antrag.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )


#run by typing in terminal:
# 1. pip install -r requirements.txt 
# 2. streamlit run app.py
# 3. to stop the server, press Ctrl+C in the terminal
