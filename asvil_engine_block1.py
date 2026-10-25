import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(
    title="Asvil Galaxy Finserv - Social Media Automation Engine",
    version="1.2.0"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
META_SYSTEM_TOKEN = os.getenv("META_SYSTEM_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class PostRequest(BaseModel):
    topic: str
    language: str = "English"

class PublishRequest(BaseModel):
    message: str

@app.get("/")
def health_check():
    return {
        "status": "active",
        "company": "Asvil Galaxy Finserv Private Limited",
        "location": "Tadepalligudem"
    }

@app.post("/generate-post")
def generate_post(request: PostRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured.")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        You are an expert financial services copywriter for Asvil Galaxy Finserv Private Limited based in Tadepalligudem, Andhra Pradesh.
        Create an engaging social media marketing post about: {request.topic}.
        Language: {request.language}.
        Include call-to-action regarding MSME Business Loans & Personal Loans and hashtags.
        """
        response = model.generate_content(prompt)
        return {
            "status": "success",
            "topic": request.topic,
            "generated_caption": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publish-to-socials")
def publish_to_socials(request: PublishRequest):
    if not META_SYSTEM_TOKEN or not FB_PAGE_ID:
        raise HTTPException(status_code=500, detail="Meta API tokens or Page ID are missing in environment variables.")
    
    results = {}
    try:
        fb_url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
        fb_payload = {
            "message": request.message,
            "access_token": META_SYSTEM_TOKEN
        }
        fb_response = requests.post(fb_url, data=fb_payload)
        results["facebook"] = fb_response.json()
    except Exception as e:
        results["facebook"] = {"error": str(e)}

    return {
        "status": "completed",
        "publishing_results": results
    }
