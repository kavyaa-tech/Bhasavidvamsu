import streamlit as st
import av
import numpy as np
import tempfile
import requests
import base64
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

# ---- Configuration ----
SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]

LANGUAGES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Kannada": "kn-IN",
    "Gujarati": "gu-IN",
    "Bengali": "bn-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN"
}

STT_API = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_API = "https://api.sarvam.ai/translate"
TTS_API = "https://api.sarvam.ai/text-to-speech"

HEADERS = {
    "api-subscription-key": SARVAM_API_KEY,
    "Content-Type": "application/json"
}

# ---- Audio Processor ----
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        samples = frame.to_ndarray()
        self.recorded_frames.append(samples)
        return frame

# ---- Streamlit UI ----
st.title("🎙️ Bhasavidvamsu - Live Indian Language Translator")

col1, col2 = st.columns(2)
input_lang = col1.selectbox("Input Language", list(LANGUAGES.keys()), index=0)
output_lang = col2.selectbox("Output Language", list(LANGUAGES.keys()), index=1)

st.markdown("### 🔴 Record your voice below and wait for result:")

ctx = webrtc_streamer(
    key="speech",
    mode="SENDONLY",
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioProcessor,
)

if ctx and ctx.audio_processor and st.button("Process Audio"):
    # Save to WAV
    audio_data = np.concatenate(ctx.audio_processor.recorded_frames, axis=1).flatten().astype(np.int16)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_data.tobytes())
        wav_path = f.name

    # ---- Speech to Text ----
    st.info("🔍 Converting speech to text...")
    with open(wav_path, "rb") as f:
        stt_response = requests.post(
            STT_API,
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": ("audio.wav", f, "audio/wav")},
            data={"language_code": LANGUAGES[input_lang]}
        )

    os.remove(wav_path)

    if stt_response.status_code != 200:
        st.error("Speech-to-text failed.")
        st.json(stt_response.json())
        st.stop()

    transcript = stt_response.json().get("transcript", "").strip()
    if not transcript:
        st.warning("Could not transcribe audio.")
        st.stop()

    st.success(f"Transcribed: {transcript}")

    # ---- Translate ----
    st.info("Translating...")
    translate_response = requests.post(
        TRANSLATE_API,
        headers=HEADERS,
        json={
            "input": transcript,
            "source_language_code": LANGUAGES[input_lang],
            "target_language_code": LANGUAGES[output_lang]
        }
    )

    if translate_response.status_code != 200:
        st.error("Translation failed.")
        st.json(translate_response.json())
        st.stop()

    translated_text = translate_response.json().get("translated_text", "").strip()
    st.success(f"Translated: {translated_text}")

    # ---- Text to Speech ----
    st.info("Generating audio...")
    tts_response = requests.post(
        TTS_API,
        headers=HEADERS,
        json={"text": translated_text, "target_language_code": LANGUAGES[output_lang]}
    )

    if tts_response.status_code != 200:
        st.error("Text-to-speech failed.")
        st.json(tts_response.json())
        st.stop()

    audio_b64 = tts_response.json().get("audios", [None])[0]
    if not audio_b64:
        st.error("No audio returned.")
        st.stop()

    st.markdown(
        f"""
        <audio autoplay controls>
            <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True,
    )
