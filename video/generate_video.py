import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

# It's recommended to use environment variables for API keys
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("Warning: API_KEY not found. Please create a .env file and add your API_KEY.")
    exit()

# Base config for video generation
MODEL_NAME = "veo-3.0-fast-generate-001"
PREDICT_URL = f"https://api.thucchien.ai/gemini/v1beta/models/{MODEL_NAME}:predictLongRunning"
OPERATION_BASE_URL = "https://api.thucchien.ai/gemini/v1beta/"

def generate_video(prompt, negative_prompt="blurry, low quality", aspect_ratio="16:9", resolution="720p"):
    """
    Sends a request to start the video generation process.
    """
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY,
    }
    data = {
        "instances": [{
            "prompt": prompt,
            "image": None
        }],
        "parameters": {
            "negativePrompt": negative_prompt,
            "aspectRatio": aspect_ratio,
            "resolution": resolution,
            "personGeneration": "allow_all"
        }
    }
    response = requests.post(PREDICT_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def check_operation_status(operation_name):
    """
    Checks the status of the video generation operation.
    """
    status_url = f"{OPERATION_BASE_URL}{operation_name}"
    headers = {
        "x-goog-api-key": API_KEY,
    }
    response = requests.get(status_url, headers=headers)
    response.raise_for_status()
    return response.json()

def download_video(video_uri, output_filename="my_generated_video.mp4"):
    """
    Downloads the video from the given URI.
    """
    download_url = video_uri.replace("https://generativelanguage.googleapis.com/v1beta/files/", "https://api.thucchien.ai/gemini/download/v1beta/files/")
    headers = {
        "x-goog-api-key": API_KEY,
    }
    print(f"Downloading video from: {download_url}")
    response = requests.get(download_url, headers=headers, stream=True)
    response.raise_for_status()

    output_path = os.path.join("video", "output", output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Video downloaded successfully and saved to {output_path}")
    return output_path

if __name__ == "__main__":
    prompt_text = "A cinematic shot of a baby raccoon wearing a tiny cowboy hat, riding a miniature pony through a field of daisies at sunset."
    print("Starting video generation for prompt:", prompt_text)
    
    try:
        prediction_response = generate_video(prompt_text)
        operation_name = prediction_response.get("name")
        if not operation_name:
            print("Error: Could not get operation name from response.")
            print(prediction_response)
        else:
            print(f"Video generation started. Operation name: {operation_name}")
            
            while True:
                status_response = check_operation_status(operation_name)
                if status_response.get("done"):
                    print("Video generation complete.")
                    video_uri = status_response["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
                    download_video(video_uri)
                    break
                else:
                    print("Video generation in progress, checking again in 10 seconds...")
                    time.sleep(10)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
