import requests
import base64
import wave
import os
import argparse
from dotenv import load_dotenv

PROMPT = """
Make Speaker1 is young and Speaker2 is old.
Speaker1: Chào mừng quý vị và các bạn đã quay trở lại với kênh podcast "Kết Nối Thế Hệ", nơi chúng ta cùng nhau chia sẻ và lắng nghe những câu chuyện giúp thu hẹp khoảng cách giữa các thế hệ trong gia đình.
Speaker2: Chào cháu Hoàng, chào quý vị thính giả. Nghe bác Hùng nói mà tôi thấy thương quá, y hệt như mình vậy. Câu chuyện của tôi thì không phải là đi khám bệnh, mà là với cái định danh điện tử VNeID.
"""

load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser(description="Generate audio from text using a multi-speaker TTS API.")
parser.add_argument("-o", "--output", default="./voice/output/multiple_speakers.wav", help="Output audio file path (default: ./voice/output/multiple_speakers.wav)")
args = parser.parse_args()

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
          {"text": PROMPT}
        ]
      }],
      "generationConfig": {
          "responseModalities": ["AUDIO"],
          "speechConfig": {
            "multiSpeakerVoiceConfig": {
              "speakerVoiceConfigs": [{
                  "speaker": "Speaker1",
                  "voiceConfig": {
                    "prebuiltVoiceConfig": {
                      "voiceName": "Kore"
                    }
                  }
                }, {
                  "speaker": "Speaker2",
                  "voiceConfig": {
                    "prebuiltVoiceConfig": {
                      "voiceName": "Puck"
                    }
                  }
                }]
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
        with wave.open(args.output, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit PCM (L16)
            wav_file.setframerate(24000)
            wav_file.writeframes(audio_data)
            print(f"Audio content written to file '{args.output}'")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
