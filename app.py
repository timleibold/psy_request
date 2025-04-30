import streamlit as st
import tempfile
import os

from audio_recorder_streamlit import audio_recorder
from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx

st.title("Psychotherapie-Antrag Generator")

st.markdown("""
1. Nehmen Sie eine WAV-Datei auf oder laden Sie sie hoch.
2. Die Datei wird in ein Transkript umgewandelt.
3. Daraus wird automatisch ein Antragsentwurf erzeugt und als DOCX-Datei bereitgestellt.
""")

st.markdown("### Audioaufnahme starten")
audio_bytes = audio_recorder(text="Aufnahme starten", recording_color="#e8b62c", neutral_color="#6aa36f", icon_size="2x")

if audio_bytes is not None:
    # Speichern der aufgenommenen Datei temporär
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        temp_wav_path = tmp_file.name

    st.success("Datei erfolgreich aufgenommen.")

    with st.spinner("Erzeuge Transkript..."):
        transcript = create_transcript(temp_wav_path)
        st.text_area("Transkript", transcript, height=300)

    with st.spinner("Erzeuge Rohfassung des Antrags..."):
        llm = LLMCall()
        json_output = llm(transcript)
        st.json(json_output)

    with st.spinner("Erzeuge DOCX-Datei..."):
        docx_path = create_docx(json_output)

    with open(docx_path, "rb") as file:
        st.download_button("DOCX herunterladen", file, file_name="antrag.docx")

    # Temporäre Datei entfernen
    os.remove(temp_wav_path)
