import streamlit as st
from functions.create_transcript import create_transcript
from functions.llm_call import LLMCall
from functions.create_docx import create_docx

from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av, numpy as np, soundfile as sf

st.set_page_config(page_title="Psychotherapie‐Antrag Generator", layout="centered")
st.title("📝 Psychotherapie‐Memo aufnehmen und Antrag erstellen")

# Initialize flag for completed recording
if "recording_done" not in st.session_state:
    st.session_state["recording_done"] = False

class Recorder(AudioProcessorBase):
    def __init__(self):
        self.frames = []
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Store incoming audio frames without sending them back
        arr = frame.to_ndarray().T  # shape: (samples, channels)
        self.frames.append(arr)
        return None
    def on_stop(self):
        # Called when user stops recording
        data = np.concatenate(self.frames, axis=0)
        # Overwrite a single memo.wav on each stop
        sf.write("memo.wav", data, samplerate=48000)
        # Mark that recording is ready
        st.session_state["recording_done"] = True
        st.success("Aufnahme gespeichert als memo.wav")

webrtc_ctx = webrtc_streamer(
    key="recorder",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=Recorder,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

if webrtc_ctx.state.playing:
    st.info("Aufnahme läuft… Klicke Stop, um zu beenden.")

# Nach Stopp der Aufnahme: Transkribieren-Button zeigen
if st.session_state.get("recording_done"):
    if st.button("Transkribieren"):  # Transkriptionsschritt
        with open("memo.wav", "rb") as wav_file:
            transcript = create_transcript(wav_file)
        st.session_state["transcript"] = transcript
        st.success("Transkription abgeschlossen")
        # Zurücksetzen für nächste Aufnahme
        st.session_state["recording_done"] = False

# If transcript is ready, display and process
if "transcript" in st.session_state:
    transcript = st.session_state["transcript"]
    st.subheader("🎧 Transkript")
    st.text_area("", transcript, height=200)
    st.info("Erstelle Psychotherapie‐Antrag…")
    antrag_json = LLMCall(transcript)
    st.subheader("📄 Antrag als JSON")
    st.json(antrag_json)
    doc_path = "Psychotherapie_Antrag.docx"
    create_docx(antrag_json, doc_path)
    with open(doc_path, "rb") as doc_file:
        st.download_button(
            label="💾 Word-Dokument herunterladen",
            data=doc_file,
            file_name="Psychotherapie_Antrag.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
