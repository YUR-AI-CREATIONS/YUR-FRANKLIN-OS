
```python
import os
import asyncio
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

# Load keys
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")
XAI_KEY = os.getenv("XAI_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SETUP CLIENTS ---
try:
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel('gemini-pro')
    if OPENAI_KEY:
        openai_client = OpenAI(api_key=OPENAI_KEY)
    if XAI_KEY:
        xai_client = OpenAI(api_key=XAI_KEY, base_url="https://api.x.ai/v1")
except Exception as e:
    print(f"Startup Warning: {e}")

# --- READ RULES LOCALLY ---
def get_bid_rules():
    # Just look for the file right next to this script
    if os.path.exists("mapping.txt"):
        with open("mapping.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "NO BID MAPPING FOUND."

# --- AGENTS ---
async def call_gemini(p):
    try: return (await asyncio.to_thread(gemini_model.generate_content, p)).text
    except Exception as e: return f"Gemini Error: {e}"

async def call_gpt(p):
    try: return (await asyncio.to_thread(openai_client.chat.completions.create, model="gpt-4-turbo", messages=[{"role":"user","content":p}])).choices[0].message.content
    except Exception as e: return f"GPT Error: {e}"

async def call_grok(p):
    try: return (await asyncio.to_thread(xai_client.chat.completions.create, model="grok-beta", messages=[{"role":"user","content":p}])).choices[0].message.content
    except Exception as e: return f"Grok Error: {e}"

# --- EXECUTION ---
@app.post("/execute")
async def execute_mission(prompt: str = Form(...), files: List[UploadFile] = File(default=None)):
    
    # 1. Read Local Rules
    master_rules = get_bid_rules()
    
    # 2. Process Files (In Memory)
    file_context = ""
    if files:
        for file in files:
            content = await file.read()
            try:
                text = content.decode("utf-8")
                file_context += f"\n--- FILE: {file.filename} ---\n{text}\n"
            except:
                file_context += f"\n--- FILE: {file.filename} (Binary) ---\n"
    
    # 3. The Prompt
    god_prompt = f"""
    [BID MAPPING / RULES]
    {master_rules}

    [PROJECT FILES]
    {file_context}

    [USER COMMAND]
    {prompt}
    """

    # 4. Fire Trinity
    results = await asyncio.gather(
        call_gemini(god_prompt),
        call_gpt(god_prompt),
        call_grok(god_prompt)
    )

    return { "gemini": results[0], "gpt": results[1], "grok": results[2] }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

