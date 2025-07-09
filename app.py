import streamlit as st
import os
from functions_local.record_audio import record_audio
from functions_local.create_transcript import transcribe_full
from functions_local.llm_call_local import LLMCall
from functions_local.create_docx import create_docx

# --- App Layout ---
st.set_page_config(page_title="Psychotherapie Antrag Assistent", layout="wide")
st.title("Psychotherapie Antrag Assistent")

# Initialize session state
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'llm_output' not in st.session_state:
    st.session_state.llm_output = None
if 'docx_path' not in st.session_state:
    st.session_state.docx_path = None

# --- Step 1: Audio Input ---
st.header("Schritt 1: Audio-Memo aufnehmen oder hochladen")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Option A: Neue Memo aufnehmen")
    duration = st.number_input("Aufnahmedauer (in Sekunden):", min_value=1, max_value=300, value=10)
    if st.button("Aufnahme starten"):
        output_filename = "memo.wav"
        with st.spinner(f"Nehme für {duration} Sekunden auf..."):
            record_audio(output_filename, duration)
        st.session_state.audio_path = output_filename
        st.success(f"Aufnahme gespeichert als {output_filename}")

with col2:
    st.subheader("Option B: Vorhandene Memo hochladen")
    uploaded_file = st.file_uploader("Wähle eine WAV-Datei", type=['wav'])
    if uploaded_file is not None:
        # Save the uploaded file to disk so that whisper can access it by path
        output_filename = uploaded_file.name
        with open(output_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.audio_path = output_filename
        st.success(f"Datei {output_filename} hochgeladen.")

# --- Step 2 & 3: Transcription and LLM Processing ---
if st.session_state.audio_path:
    st.header("Schritt 2: Transkription und Antragerstellung")
    st.write(f"Audio-Datei: `{st.session_state.audio_path}`")

    if st.button("Antrag aus Audio erstellen"):
        # Step 2: Transcription
        with st.spinner("Transkription wird erstellt... (dies kann einige Minuten dauern)"):
            try:
                st.session_state.transcript = transcribe_full(st.session_state.audio_path)
            except Exception as e:
                st.error(f"Fehler bei der Transkription: {e}")
        
        if st.session_state.transcript:
            st.subheader("Erstelltes Transkript:")
            st.text_area("Transkript", st.session_state.transcript, height=200)

            # Step 3: LLM Call
            with st.spinner("Strukturierter Antrag wird mit LLM erstellt... (dies kann einige Minuten dauern)"):
                try:
                    st.session_state.llm_output = LLMCall(st.session_state.transcript)
                except Exception as e:
                    st.error(f"Fehler beim LLM-Aufruf: {e}")

# --- Step 4: Document Generation & Download ---
if st.session_state.llm_output:
    st.header("Schritt 3: Dokument generieren")
    st.subheader("Strukturierter Antrag (JSON):")
    st.json(st.session_state.llm_output)

    if st.button("DOCX-Dokument erstellen"):
        with st.spinner("DOCX-Datei wird erstellt..."):
            try:
                doc_path = "Psychotherapie_Antrag.docx"
                create_docx(st.session_state.llm_output, doc_path)
                st.session_state.docx_path = doc_path
                st.success(f"Dokument '{doc_path}' erfolgreich erstellt!")
            except Exception as e:
                st.error(f"Fehler beim Erstellen der DOCX-Datei: {e}")

if st.session_state.docx_path:
    with open(st.session_state.docx_path, "rb") as f:
        st.download_button(
            label="DOCX-Datei herunterladen",
            data=f,
            file_name=os.path.basename(st.session_state.docx_path),
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )