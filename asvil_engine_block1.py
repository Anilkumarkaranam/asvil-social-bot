import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(
    title="Asvil Galaxy Finserv - Social Media Automation Engine",
    version="1.5.0"
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

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Asvil Social Bot - Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f4f6f9; color: #333; }
            .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            h2 { color: #1a365d; margin-top: 0; }
            label { font-weight: bold; display: block; margin-top: 15px; }
            input[type="text"], textarea { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            textarea { height: 120px; }
            button { background: #2563eb; color: white; border: none; padding: 12px 20px; margin-top: 15px; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background: #1d4ed8; }
            #status { margin-top: 20px; padding: 12px; border-radius: 4px; white-space: pre-wrap; display: none; }
            .success { background: #d1fae5; color: #065f46; border: 1px solid #10b981; }
            .error { background: #fee2e2; color: #991b1b; border: 1px solid #ef4444; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Asvil Galaxy Finserv - Social Bot</h2>
            <p>Enter a topic below to generate marketing copy and publish directly to Facebook.</p>
            
            <label for="topicInput">Post Topic:</label>
            <input type="text" id="topicInput" value="MSME Business Loans for expanding local trade in Tadepalligudem">
            
            <button onclick="generateAndPublish()">Generate & Publish to Facebook</button>
            
            <label for="outputBox">Generated Caption & Status:</label>
            <textarea id="outputBox" placeholder="Result will appear here..."></textarea>
            
            <div id="status"></div>
        </div>

        <script>
            async function generateAndPublish() {
                const topic = document.getElementById('topicInput').value;
                const statusDiv = document.getElementById('status');
                const outputBox = document.getElementById('outputBox');
                
                statusDiv.style.display = 'block';
                statusDiv.className = '';
                statusDiv.innerText = 'Generating caption with Gemini...';
                outputBox.value = '';

                try {
                    // Step 1: Generate Post
                    const genRes = await fetch('/generate-post', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ topic: topic, language: 'English' })
                    });
                    const genData = await genRes.json();
                    
                    if (!genRes.ok) throw new Error(genData.detail || 'Generation failed');
                    
                    const caption = genData.generated_caption;
                    outputBox.value = caption;
                    
                    statusDiv.innerText = 'Publishing to Facebook...';

                    // Step 2: Publish to Facebook
                    const pubRes = await fetch('/publish-to-socials', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: caption })
                    });
                    const pubData = await pubRes.json();

                    if (!pubRes.ok) throw new Error(pubData.detail || 'Publishing failed');

                    statusDiv.className = 'success';
                    statusDiv.innerText = 'Successfully published to Facebook!';
                } catch (err) {
                    statusDiv.className = 'error';
                    statusDiv.innerText = 'Error: ' + err.message;
                }
            }
        </script>
    </body>
    </html>
    """

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
