import streamlit as st
import requests
import base64
import tempfile
import os
import logging
from streamlit_audio_recorder import audio_recorder

# ------------------- CONFIG -------------------
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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ------------------- FUNCTIONS -------------------
def save_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        return f.name

def speech_to_text(wav_path, language_code):
    with open(wav_path, "rb") as f:
        response = requests.post(
            STT_API,
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": ("audio.wav", f, "audio/wav")},
            data={"language_code": language_code}
        )
    os.remove(wav_path)
    return response

def text_to_audio(text, language_code):
    payload = {
        "text": text,
        "target_language_code": language_code
    }
    response = requests.post(TTS_API, headers=HEADERS, json=payload)

    if response.status_code != 200:
        st.error("Text-to-speech failed.")
        st.json(response.json())
        return None

    data = response.json()
    audio_b64 = data.get("audios", [None])[0]

    if not audio_b64:
        st.error("No audio data in response.")
        return None

    audio_html = f"""
    <audio autoplay controls>
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    return base64.b64decode(audio_b64)

# ------------------- UI -------------------
st.title("🎙️ Bhasavidvamsu - Live Indian Language Translator")
st.markdown("Speak in one Indian language and get live translation + voice output in another.")

col1, col2 = st.columns(2)
input_lang = col1.selectbox("Input Language", list(LANGUAGES.keys()), index=0)
output_lang = col2.selectbox("Output Language", list(LANGUAGES.keys()), index=1)

st.markdown("### 🔴 Record your voice")
audio_bytes = audio_recorder()

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.success("Audio captured successfully!")

    # Save to file
    wav_path = save_audio(audio_bytes)

    # STT
    st.write("Converting speech to text...")
    response = speech_to_text(wav_path, LANGUAGES[input_lang])

    if response.status_code != 200:
        st.error("Speech-to-text failed.")
        st.json(response.json())
        st.stop()

    transcript = response.json().get("transcript", "").strip()
    if not transcript:
        st.warning("Could not transcribe audio.")
        st.stop()

    st.success(f"Transcribed: {transcript}")

    # Translation
    st.write("Translating...")
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
    if not translated_text:
        st.warning("No translated text.")
        st.stop()

    st.success(f"Translated: {translated_text}")

    # TTS
    st.write("Generating audio...")
    text_to_audio(translated_text, LANGUAGES[output_lang])

else:
    st.info("Click the red microphone button to start recording.")
