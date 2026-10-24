import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="Asvil 24/7 Social Media Engine")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
META_SYSTEM_TOKEN = os.getenv("META_SYSTEM_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class PostRequest(BaseModel):
    topic: str
    language: str = "English"

@app.get("/")
def health_check():
    return {"status": "active", "company": "Asvil Galaxy Finserv Private Limited", "location": "Tadepalligudem"}

@app.post("/generate-post")
def generate_post(data: PostRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key missing")
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Create a professional social media caption for Asvil Galaxy Finserv offering loans (Personal, Business, Doctor, Home, LAP, Vehicle) about {data.topic}. Language: {data.language}. Pure separation: if Telugu, use pure Telugu script only without English mixing."
    
    response = model.generate_content(prompt)
    return {"caption": response.text, "language": data.language}