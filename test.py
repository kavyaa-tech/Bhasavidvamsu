import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import requests
import numpy as np
import base64
import tempfile
import os
import logging

# ------------------- CONFIG -------------------
SARVAM_API_KEY = "sk_e9vie8e9_ekhJZPn5vux8GrjRRBRVf5vv"  # <-- Put your API key here

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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ------------------- RECORD FUNCTION -------------------
def record_audio(duration=6, fs=16000):
    logger.debug("Starting audio recording...")
    st.info(f"Recording for {duration} seconds at {fs} Hz...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    st.success("Recording complete.")
    logger.debug("Audio recording completed.")
    return audio, fs

def save_wav(audio, fs):
    logger.debug("Saving audio to temporary file...")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        write(tmp_file.name, fs, audio)
        logger.debug(f"Saved audio to {tmp_file.name}")
        return tmp_file.name

def speech_to_text(wav_path, language_code):
    logger.debug(f"Sending audio to STT API for language {language_code}...")
    with open(wav_path, "rb") as f:
        response = requests.post(
            STT_API,
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": ("audio.wav", f, "audio/wav")},
            data={"language_code": language_code}
        )
    try:
        os.remove(wav_path)
        logger.debug(f"Deleted temporary file {wav_path}")
    except Exception as e:
        logger.warning(f"Failed to delete {wav_path}: {str(e)}")
    logger.debug("STT API call completed.")
    return response

def text_to_audio(text, language_code):
    logger.debug(f"Generating TTS for text: {text} in language {language_code}")
    payload = {
        "text": text,
        "target_language_code": language_code
    }
    try:
        response = requests.post(TTS_API, headers=HEADERS, json=payload)
        logger.debug(f"TTS API response status: {response.status_code}")
    except Exception as e:
        st.error("Error contacting TTS API.")
        st.text(f"Error: {str(e)}")
        logger.error(f"TTS API call failed: {str(e)}")
        return None

    if response.status_code != 200:
        st.error("Text-to-speech failed.")
        st.json(response.json())
        logger.error(f"TTS failed with status {response.status_code}: {response.text}")
        return None

    try:
        data = response.json()
        audios = data.get("audios", [])
        if not audios:
            st.error("No audio data found in the response.")
            logger.error("No audio data in TTS response")
            return None

        audio_b64 = audios[0]
        audio_bytes = base64.b64decode(audio_b64)
        logger.debug("Audio data decoded successfully.")
    except Exception as e:
        st.error("Error processing TTS response.")
        st.text(f"Error: {str(e)}")
        logger.error(f"Error processing TTS response: {str(e)}")
        return None

    # Show autoplay audio
    audio_html = f"""
    <audio autoplay controls>
      <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
      Your browser does not support the audio element.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    logger.debug("Autoplay audio displayed.")

    return audio_bytes

# ------------------- UI ------------------
st.title("🎙️Bhasavidvamsu - Live Indian Language Translator")
st.markdown("Speak in one Indian language and get live translation + voice output in another.")

# Initialize session state
if 'input_language' not in st.session_state:
    st.session_state.input_language = "English"
if 'output_language' not in st.session_state:
    st.session_state.output_language = "Hindi"
if 'duration' not in st.session_state:
    st.session_state.duration = 4

col1, col2 = st.columns(2)
with col1:
    input_lang = st.selectbox("Input Language", list(LANGUAGES.keys()), 
                             index=list(LANGUAGES.keys()).index(st.session_state.input_language),
                             key="input_lang_select")
    st.session_state.input_language = input_lang
with col2:
    output_lang = st.selectbox("Output Language", list(LANGUAGES.keys()),
                              index=list(LANGUAGES.keys()).index(st.session_state.output_language),
                              key="output_lang_select")
    st.session_state.output_language = output_lang

duration = st.slider("Recording Duration (seconds)", 2, 6, st.session_state.duration, 
                    key="duration_slider")
st.session_state.duration = duration

# ------------------- RECORD, TRANSLATE, SPEAK -------------------
if st.button("Record & Translate", key="translate"):
    try:
        logger.debug("Starting translation process...")

        # Record audio
        audio, fs = record_audio(duration=duration)

        # Save to .wav file
        wav_path = save_wav(audio, fs)

        # ------------------- STT -------------------
        st.write("Converting speech to text...")
        try:
            response = speech_to_text(wav_path, LANGUAGES[input_lang])
        except Exception as e:
            st.error("Error contacting STT API.")
            st.text(str(e))
            logger.error(f"STT API error: {str(e)}")
            st.stop()

        if response.status_code != 200:
            st.error("❌ Speech-to-text failed.")
            st.json(response.json())
            logger.error(f"STT failed: {response.text}")
            st.stop()

        transcript = str(response.json().get("transcript", "")).strip()

        if not transcript:
            st.error("Could not understand speech. Please try again.")
            logger.warning("Empty STT transcript")
            st.stop()

        st.success(f"Transcribed: {transcript}")
        logger.debug(f"Transcribed text: {transcript}")

        # ------------------- TRANSLATE -------------------
        st.write("Translating text...")
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
            logger.error(f"Translation failed: {translate_response.text}")
            st.stop()

        translated_text = translate_response.json().get("translated_text", "").strip()

        if not translated_text:
            st.error("Translation returned empty text.")
            logger.warning("Empty translated text")
            st.stop()

        st.success(f"Translated: {translated_text}")
        logger.debug(f"Translated text: {translated_text}")

        # ------------------- TTS -------------------
        st.write("Generating speech in output language...")
        audio_bytes = text_to_audio(translated_text, LANGUAGES[output_lang])
        if audio_bytes:
            st.success("✅ Translation + voice output complete!")
            logger.debug("TTS completed successfully.")
        else:
            logger.warning("TTS failed to produce audio")

    except Exception as e:
        st.error("An unexpected error occurred.")
        st.text(f"Error: {str(e)}")
        logger.error(f"Unexpected error in main loop: {str(e)}")

st.info("Ready for the next recording. Click 'Record & Translate' to start.")
logger.debug("App reached end of cycle, still running.")
