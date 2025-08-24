import os
from dotenv import load_dotenv
from openai import OpenAI
import whisper
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# === Load API Key ===
load_dotenv()
OPENAI_API_KEY = OpenAI()

# === Load Whisper model ===
model = whisper.load_model("base")

app = FastAPI()

# Serve static files (gif, css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask(file: UploadFile):
    # Save uploaded file
    filepath = "voice_input.wav"
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Transcribe with Whisper
    result = model.transcribe(filepath)
    transcribed_text = result["text"]

    # Ask GPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": transcribed_text}]
    )
    reply = response.choices[0].message.content.strip()

    return {"you_said": transcribed_text, "gpt_reply": reply}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
