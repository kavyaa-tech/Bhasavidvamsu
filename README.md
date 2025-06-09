🎙️ Bhasavidvamsu - Live Indian Language Translator
Bhasavidvamsu is a Streamlit-based application that allows users to speak in one Indian language and receive a translated voice output in another Indian language, in real-time!
It combines speech-to-text, machine translation, and text-to-speech into a seamless pipeline powered by Sarvam.ai APIs.

🚀 Features
🎤 Record speech using your microphone

📝 Convert spoken words into text via Speech-to-Text

🌐 Translate the text between Indian languages

🔊 Hear the translated output via Text-to-Speech

⚙️ Easy-to-use interface built with Streamlit

🗣️ Supported Languages
English (en-IN)

Hindi (hi-IN)

Tamil (ta-IN)

Telugu (te-IN)

Kannada (kn-IN)

Gujarati (gu-IN)

Bengali (bn-IN)

Malayalam (ml-IN)

Marathi (mr-IN)

🛠️ Tech Stack
Python

Streamlit for UI

sounddevice + scipy for audio capture and processing

Sarvam.ai APIs:

Speech-to-Text (STT)

Translate

Text-to-Speech (TTS)

🔧 Setup Instructions
Clone the Repository

bash
Copy
Edit
git clone https://github.com/yourusername/bhasavidvamsu.git
cd bhasavidvamsu
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Get an API Key from Sarvam.ai
Add your API key to the script:

python
Copy
Edit
SARVAM_API_KEY = "your_api_key_here"
Run the App

bash
Copy
Edit
streamlit run app.py
📸 Screenshots
Record Speech	Translated Output

📄 License
This project is licensed under the MIT License.

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

✨ Acknowledgements
Streamlit

Sarvam.ai

The incredible open-source Python community 🙌
