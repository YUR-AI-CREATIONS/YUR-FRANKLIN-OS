import os
import time
from typing import Optional

try:
    from google import genai
    from google.cloud import texttospeech
    from google.auth import default
except Exception:
    genai = None
    texttospeech = None
    default = None


def _make_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not genai or not api_key:
        raise RuntimeError("Gemini client not available (missing SDK or GEMINI_API_KEY).")
    return genai.Client(api_key=api_key)


def _make_tts_client():
    if not texttospeech or not default:
        raise RuntimeError("Google TTS not available (missing SDK).")
    creds, _ = default()
    return texttospeech.TextToSpeechClient(credentials=creds)


def generate_text(prompt: str):
    start = time.time()
    client = _make_gemini_client()
    response = client.models.generate_content(model="models/gemini-2.5-pro", contents=prompt)
    text = getattr(response, "text", "")
    return {"engine": "Gemini", "text": text, "latency": round(time.time() - start, 2), "confidence": 0.9}


def generate_image(prompt: str, out_path: str = "output_image.png"):
    start = time.time()
    client = _make_gemini_client()
    response = client.models.generate_images(model="models/imagen-4.0-ultra-generate-001", prompt=prompt)
    image_bytes = response.generated_images[0].image.image_bytes
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    return {"engine": "Gemini", "path": out_path, "latency": round(time.time() - start, 2), "confidence": 0.9}


def generate_video(prompt: str, out_path: str = "output_video.mp4"):
    start = time.time()
    client = _make_gemini_client()
    operation = client.models.generate_videos(model="models/veo-3.1-generate-preview", prompt=prompt)
    result = operation.result()
    video_bytes = result.videos[0].video_bytes
    with open(out_path, "wb") as f:
        f.write(video_bytes)
    return {"engine": "Gemini", "path": out_path, "latency": round(time.time() - start, 2), "confidence": 0.9}


def generate_audio(prompt: str, out_path: str = "output_audio.mp3"):
    start = time.time()
    tts = _make_tts_client()
    synthesis_input = texttospeech.SynthesisInput(text=prompt)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Studio-O")
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open(out_path, "wb") as out:
        out.write(response.audio_content)
    return {"engine": "Gemini", "path": out_path, "latency": round(time.time() - start, 2), "confidence": 0.9}


def generate_embedding(prompt: str):
    start = time.time()
    client = _make_gemini_client()
    embedding = client.models.embed_content(model="models/text-embedding-004", contents=prompt)
    vec = getattr(embedding, "embedding", None)
    length = len(vec.values) if vec and hasattr(vec, "values") else None
    return {"engine": "Gemini", "embedding_length": length, "latency": round(time.time() - start, 2), "confidence": 0.9}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gemini Multimodal AI Control Script")
    parser.add_argument("--mode", type=str, required=True, help="Mode: text | image | video | audio | embed")
    parser.add_argument("--prompt", type=str, required=True, help="Prompt or input text")
    args = parser.parse_args()

    mode = args.mode.lower()
    prompt = args.prompt

    if mode == "text":
        res = generate_text(prompt)
        print(res.get("text"))
    elif mode == "image":
        res = generate_image(prompt)
        print(f"✅ Image saved as {res.get('path')}")
    elif mode == "video":
        res = generate_video(prompt)
        print(f"✅ Video saved as {res.get('path')}")
    elif mode == "audio":
        res = generate_audio(prompt)
        print(f"✅ Audio saved as {res.get('path')}")
    elif mode == "embed":
        res = generate_embedding(prompt)
        print(f"✅ Embedding vector length: {res.get('embedding_length')}")
    else:
        print("❌ Invalid mode. Use: text | image | video | audio | embed")


if __name__ == "__main__":
    main()
