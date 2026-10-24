import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

# Initialize FastAPI app
app = FastAPI(
    title="Asvil Galaxy Finserv - Social Media Automation Engine",
    version="1.0.0"
)

# Configure Google Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Request schema for post generation
class PostRequest(BaseModel):
    topic: str
    language: str = "English"

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
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured in environment variables.")
    
    try:
        # Using gemini-pro which is universally supported
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"""
        You are an expert financial services copywriter and social media manager for Asvil Galaxy Finserv Private Limited based in Tadepalligudem, Andhra Pradesh.
        Create an engaging, professional social media marketing post (suitable for Facebook and Instagram) about: {request.topic}.
        Language: {request.language}.
        Include compelling hooks, clear call-to-action regarding loan assistance (Personal Loans & MSME Business Loans), and relevant hashtags.
        """
        
        response = model.generate_content(prompt)
        return {
            "status": "success",
            "topic": request.topic,
            "language": request.language,
            "generated_caption": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
