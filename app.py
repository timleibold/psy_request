import streamlit as st
from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx

st.set_page_config(page_title="Psychotherapie‐Antrag Generator", layout="centered")
st.title("📝 Psychotherapie‐Memo aufnehmen und Antrag erstellen")

from audio_recorder_streamlit import audio_recorder

# --- Browser-based audio recorder ---
audio_bytes = audio_recorder()
if audio_bytes:
    # Save recording to file
    with open("memo.wav", "wb") as f:
        f.write(audio_bytes)
    # 1) Transcription
    transcript = create_transcript(open("memo.wav", "rb"))
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
