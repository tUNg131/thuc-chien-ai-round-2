import requests
import base64
import wave
import os
from dotenv import load_dotenv

load_dotenv()

# Load the API key from the environment variable
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("API_KEY not found in .env file. Please create a .env file and add your API key.")
else:
    url = "https://api.thucchien.ai/gemini/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"

    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json",
    }

    data = {
      "contents": [{
        "parts": [
          {"text": "Chào bạn mình tên là Tùng!"}
        ]
      }],
      "generationConfig": {
          "responseModalities": ["AUDIO"],
          "speechConfig": {
            "voiceConfig": {
              "prebuiltVoiceConfig": {
                "voiceName": "Kore"
              }
            }
          }
      }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        audio_data_base64 = response_json['candidates'][0]['content']['parts'][0]['inlineData']['data']
        audio_data = base64.b64decode(audio_data_base64)

        # The mime_type is "audio/L16;codec=pcm;rate=24000", which means raw PCM audio.
        # We'll save it as a WAV file.
        with wave.open("./voice/output/single_speaker.wav", "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit PCM (L16)
            wav_file.setframerate(24000)
            wav_file.writeframes(audio_data)
            print("Audio content written to file 'voice/output/single_speaker.wav'")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
