# 🎙️ Bhasavidvamsu - Live Indian Language Translator

**Bhasavidvamsu** is a Streamlit-based application that allows users to **speak in one Indian language** and receive a **translated voice output** in another Indian language — in real-time!  
It combines **speech-to-text**, **machine translation**, and **text-to-speech** into a seamless pipeline powered by **Sarvam.ai APIs**.

---

## 🚀 Features

- 🎤 Record speech using your microphone
- 📝 Convert spoken words into text via **Speech-to-Text**
- 🌐 Translate the text between Indian languages
- 🔊 Hear the translated output via **Text-to-Speech**
- ⚙️ Easy-to-use interface built with **Streamlit**

---

## 🗣️ Supported Languages

- English (en-IN)  
- Hindi (hi-IN)  
- Tamil (ta-IN)  
- Telugu (te-IN)  
- Kannada (kn-IN)  
- Gujarati (gu-IN)  
- Bengali (bn-IN)  
- Malayalam (ml-IN)  
- Marathi (mr-IN)  

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** for UI
- **sounddevice** + **scipy** for audio capture and processing
- **Sarvam.ai APIs**:
  - Speech-to-Text (STT)
  - Translate
  - Text-to-Speech (TTS)

---

## 🔧 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kavyaa-tech/bhasavidvamsu.git
   cd bhasavidvamsu

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt

3. **Get an API Key from Sarvam.ai**
    Add your API key to the script:
   ```bash
   SARVAM_API_KEY = "your_api_key_here"

4. **Run the App**
    ```bash
    streamlit run test.py

**📸 Screenshots**
![image](https://github.com/user-attachments/assets/4dd8323f-b867-4127-89aa-a0a7d36876ac)


**📄 License**
This project is licensed under the MIT License.

**🤝 Contributing**
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

**✨ Acknowledgements**
Streamlit

Sarvam.ai

The incredible open-source Python community 🙌
