import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import numpy as np
import tempfile
import requests
import os
import base64
import time

# ------------- CONFIG -------------
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


# ------------- AUDIO PROCESSOR -------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame

    def get_wav_file(self):
        if not self.frames:
            return None

        # Combine all recorded audio
        audio_np = np.concatenate(self.frames)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        import soundfile as sf
        sf.write(temp_wav.name, audio_np, samplerate=frame.sample_rate, format='WAV')
        return temp_wav.name


# ------------- FUNCTIONS -------------
def transcribe_audio(file_path, lang_code):
    with open(file_path, "rb") as f:
        response = requests.post(
            STT_API,
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": ("audio.wav", f, "audio/wav")},
            data={"language_code": lang_code}
        )
    return response


def translate_text(text, src_lang, tgt_lang):
    payload = {
        "input": text,
        "source_language_code": src_lang,
        "target_language_code": tgt_lang
    }
    return requests.post(TRANSLATE_API, headers=HEADERS, json=payload)


def speak_text(text, lang_code):
    payload = {
        "text": text,
        "target_language_code": lang_code
    }
    response = requests.post(TTS_API, headers=HEADERS, json=payload)
    if response.status_code != 200:
        st.error("TTS failed.")
        return None
    audio_b64 = response.json().get("audios", [""])[0]
    audio_bytes = base64.b64decode(audio_b64)
    st.audio(audio_bytes, format="audio/wav")
    return audio_bytes


# ------------- UI -------------
st.set_page_config(page_title="Live Indian Language Translator", layout="centered")
st.title("🎙️ Bhasavidvamsu - Live Indian Language Translator")
st.markdown("Speak in one Indian language and get live translation + speech output in another.")

col1, col2 = st.columns(2)
input_lang = col1.selectbox("🎤 Input Language", list(LANGUAGES.keys()), index=0)
output_lang = col2.selectbox("🗣 Output Language", list(LANGUAGES.keys()), index=1)

st.markdown("### 🔴 Record your voice below:")

ctx = webrtc_streamer(
    key="speech",
    mode="SENDONLY",
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioProcessor,
)

if ctx.audio_processor:
    if st.button("🛑 Stop and Process"):
        st.info("Processing your speech...")

        audio_path = ctx.audio_processor.get_wav_file()
        if not audio_path:
            st.error("No audio data found.")
            st.stop()

        st.write("🧠 Converting speech to text...")
        stt_resp = transcribe_audio(audio_path, LANGUAGES[input_lang])
        if stt_resp.status_code != 200:
            st.error("Speech recognition failed.")
            st.json(stt_resp.json())
            st.stop()
        transcript = stt_resp.json().get("transcript", "").strip()
        st.success(f"Transcribed: `{transcript}`")

        st.write("🌐 Translating...")
        tr_resp = translate_text(transcript, LANGUAGES[input_lang], LANGUAGES[output_lang])
        if tr_resp.status_code != 200:
            st.error("Translation failed.")
            st.json(tr_resp.json())
            st.stop()
        translated = tr_resp.json().get("translated_text", "").strip()
        st.success(f"Translated: `{translated}`")

        st.write("🔊 Speaking...")
        speak_text(translated, LANGUAGES[output_lang])

        # Clean up temp file
        os.remove(audio_path)
