# app.py
import streamlit as st
from functions.record_audio import record_memo
from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx

st.set_page_config(page_title="Psychotherapie‐Antrag Generator", layout="centered")
st.title("📝 Psychotherapie‐Memo aufnehmen und Antrag erstellen")

# 1) Aufnahme‐Button
if st.button("🎙️ Aufnahme starten (max. 5 Minuten)"):
    st.info("Aufnahme läuft… bitte sprechen.")
    # block until finished
    record_memo("memo.wav", duration=300)
    st.success("Aufnahme beendet!")

    # 2) Transkription
    with open("memo.wav", "rb") as audio_file:
        transcript = create_transcript(audio_file)
    st.subheader("🎧 Transkript")
    st.text_area("", transcript, height=200)

    # 3) LLM‐Aufruf
    st.info("Erstelle Psychotherapie‐Antrag…")
    antrag_json = LLMCall(transcript)
    st.subheader("📄 Antrag als JSON")
    st.json(antrag_json)

    # 4) DOCX‐Erzeugung & Download
    doc_path = "Psychotherapie_Antrag.docx"
    create_docx(antrag_json, doc_path)
    with open(doc_path, "rb") as doc_file:
        st.download_button(
            label="💾 Word-Dokument herunterladen",
            data=doc_file,
            file_name="Psychotherapie_Antrag.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )