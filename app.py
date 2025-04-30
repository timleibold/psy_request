import streamlit as st
import tempfile
import os

from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx

st.title("Psychotherapie-Antrag Generator")

st.markdown("""
1. Nehmen Sie eine WAV-Datei auf oder laden Sie sie hoch.
2. Die Datei wird in ein Transkript umgewandelt.
3. Daraus wird automatisch ein Antragsentwurf erzeugt und als DOCX-Datei bereitgestellt.
""")

uploaded_file = st.file_uploader("WAV-Datei aufnehmen oder hochladen", type=["wav"])

if uploaded_file is not None:
    # Speichern der hochgeladenen Datei temporär
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_wav_path = tmp_file.name

    st.success("Datei erfolgreich hochgeladen.")

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
