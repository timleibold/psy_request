# app.py
import streamlit as st
import threading, webbrowser
import sys
from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

st.set_page_config(page_title="Psychotherapie‐Antrag Generator", layout="centered")
st.title("📝 Psychotherapie‐Memo aufnehmen und Antrag erstellen")

st.subheader("🎙️ Sprachmemo aufnehmen")

if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "recorded_audio" not in st.session_state:
    st.session_state.recorded_audio = None
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = []
if "fs" not in st.session_state:
    st.session_state.fs = 44100

col1, col2 = st.columns(2)
with col1:
    if st.button("🎙️ Aufnahme starten (lokal)"):
        st.session_state.recording = True
        st.session_state.audio_buffer = []
        st.info("Aufnahme läuft...")

with col2:
    if st.button("⏹️ Aufnahme stoppen & speichern"):
        st.session_state.recording = False
        if st.session_state.audio_buffer:
            audio_np = np.concatenate(st.session_state.audio_buffer, axis=0)
            write("aufnahme.wav", st.session_state.fs, audio_np)
            st.success("Aufnahme gespeichert als aufnahme.wav")
            st.session_state.recorded_audio = open("aufnahme.wav", "rb").read()

if st.session_state.get("recorded_audio"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(st.session_state.recorded_audio)
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
