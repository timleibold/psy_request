# app.py
import streamlit as st
import threading, webbrowser, time
import sys
from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx
from audio_recorder_streamlit import audio_recorder
import tempfile

st.set_page_config(page_title="Psychotherapie‐Antrag Generator", layout="centered")
st.title("📝 Psychotherapie‐Memo aufnehmen und Antrag erstellen")

st.subheader("🎙️ Sprachmemo aufnehmen")

if "recording" not in st.session_state:
    st.session_state.recording = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if not st.session_state.recording:
    if st.button("🎙️ Aufnahme starten"):
        st.session_state.recording = True
        st.session_state.start_time = time.time()
else:
    elapsed = int(time.time() - st.session_state.start_time)
    st.success(f"⏱ Aufnahme läuft: {elapsed} Sekunden")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.write("Aufnahme läuft...")
        with col2:
            if st.button("⏹️ Aufnahme stoppen"):
                audio_data = audio_recorder(
                    text="",
                    recording_color="#e63946",
                    neutral_color="#457b9d",
                    icon_name="microphone",
                    icon_size="6x"
                )
                st.session_state.recording = False

                if audio_data:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                        tmpfile.write(audio_data)
                        wav_path = tmpfile.name

                    # 1) Transkription
                    transcript = create_transcript(open(wav_path, "rb"))
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
