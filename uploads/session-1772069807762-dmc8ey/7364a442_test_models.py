import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("XAI_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

models = ["grok-3", "grok", "grok-latest", "grok-2-1212"]

payload = {
    "messages": [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Say hello."}
    ],
    "temperature": 0.2,
    "max_tokens": 50
}

for model in models:
    try:
        payload["model"] = model
        r = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        print(f"{model}: {r.status_code}")
        if r.status_code == 200:
            print(f"SUCCESS! Using {model}")
            print(r.json()["choices"][0]["message"]["content"][:80])
            break
        else:
            print(f"Response: {r.text[:120]}")
    except Exception as e:
        print(f"{model}: Error - {str(e)[:60]}")
