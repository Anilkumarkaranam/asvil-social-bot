import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(
    title="Asvil Galaxy Finserv - Social Media Automation Engine",
    version="2.2.0"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
META_SYSTEM_TOKEN = os.getenv("META_SYSTEM_TOKEN")
DEFAULT_FB_PAGE_ID = os.getenv("FB_PAGE_ID", "384113174785081")

class PostRequest(BaseModel):
    topic: str
    language: str = "English"

class PublishRequest(BaseModel):
    message: str
    page_id: str = None

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
            input[type="text"], textarea, select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            textarea { height: 140px; }
            button { background: #2563eb; color: white; border: none; padding: 12px 20px; margin-top: 15px; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background: #1d4ed8; }
            .secondary-btn { background: #059669; margin-top: 10px; }
            .secondary-btn:hover { background: #047857; }
            .debug-btn { background: #d97706; margin-top: 10px; }
            .debug-btn:hover { background: #b45309; }
            #status { margin-top: 20px; padding: 12px; border-radius: 4px; white-space: pre-wrap; display: none; }
            .success { background: #d1fae5; color: #065f46; border: 1px solid #10b981; }
            .error { background: #fee2e2; color: #991b1b; border: 1px solid #ef4444; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Asvil Galaxy Finserv - Social Bot</h2>
            <p>Generate AI marketing copy and publish directly to your Facebook pages.</p>
            
            <label for="pageSelect">Select Facebook Page ID:</label>
            <input type="text" id="pageSelect" value="384113174785081" placeholder="Enter FB Page ID">

            <label for="topicInput">Post Topic:</label>
            <input type="text" id="topicInput" value="MSME Business Loans for expanding local trade in Tadepalligudem">
            
            <button onclick="generateAndPublish()">Generate & Publish to Facebook</button>
            
            <label for="outputBox">Generated Caption:</label>
            <textarea id="outputBox" placeholder="Caption will appear here..."></textarea>
            
            <button class="secondary-btn" onclick="publishOnly()">Publish Text in Box to Selected Page</button>
            <button class="debug-btn" onclick="checkToken()">Diagnostic: Check Token & Pages Access</button>
            
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
                    const genRes = await fetch('/generate-post', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ topic: topic, language: 'English' })
                    });
                    const genData = await genRes.json();
                    if (!genRes.ok) throw new Error(genData.detail || 'Generation failed');
                    
                    outputBox.value = genData.generated_caption;
                    await publishOnly();
                } catch (err) {
                    statusDiv.className = 'error';
                    statusDiv.innerText = 'Error: ' + err.message;
                }
            }

            async function publishOnly() {
                const caption = document.getElementById('outputBox').value.trim();
                const pageId = document.getElementById('pageSelect').value.trim();
                const statusDiv = document.getElementById('status');

                if (!caption) {
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'error';
                    statusDiv.innerText = 'Please generate or enter text first.';
                    return;
                }

                statusDiv.style.display = 'block';
                statusDiv.className = '';
                statusDiv.innerText = 'Publishing to selected Facebook Page...';

                try {
                    const pubRes = await fetch('/publish-to-socials', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: caption, page_id: pageId })
                    });
                    const pubData = await pubRes.json();

                    if (!pubRes.ok) throw new Error(pubData.detail || 'Publishing failed');

                    const postId = pubData.publishing_results?.facebook?.id || 'Success';
                    statusDiv.className = 'success';
                    statusDiv.innerText = 'Successfully published! (Post ID: ' + postId + ')';
                } catch (err) {
                    statusDiv.className = 'error';
                    statusDiv.innerText = 'Error: ' + err.message;
                }
            }

            async function checkToken() {
                const statusDiv = document.getElementById('status');
                statusDiv.style.display = 'block';
                statusDiv.className = '';
                statusDiv.innerText = 'Checking token status with Facebook...';

                try {
                    const res = await fetch('/check-token');
                    const data = await res.json();
                    statusDiv.className = res.ok ? 'success' : 'error';
                    statusDiv.innerText = JSON.stringify(data, null, 2);
                } catch (err) {
                    statusDiv.className = 'error';
                    statusDiv.innerText = 'Diagnostic check failed: ' + err.message;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/check-token")
def check_token():
    if not META_SYSTEM_TOKEN:
        return {"status": "error", "message": "META_SYSTEM_TOKEN is empty in environment variables."}
    
    try:
        # Check token debug info
        debug_url = f"https://graph.facebook.com/v18.0/debug_token?input_token={META_SYSTEM_TOKEN}&access_token={META_SYSTEM_TOKEN}"
        debug_res = requests.get(debug_url, timeout=15).json()
        
        # Check what pages this token can see
        accounts_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={META_SYSTEM_TOKEN}"
        acc_res = requests.get(accounts_url, timeout=15).json()
        
        return {
            "token_debug_info": debug_res.get("data", debug_res),
            "accessible_pages": acc_res.get("data", acc_res)
        }
    except Exception as e:
        return {"status": "error", "exception": str(e)}

@app.post("/generate-post")
def generate_post(request: PostRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured.")
    
    prompt = (
        f"You are an expert financial services copywriter for Asvil Galaxy Finserv Private Limited "
        f"based in Tadepalligudem, Andhra Pradesh. Write an engaging, concise social media marketing post "
        f"about: {request.topic}. Language: {request.language}. "
        f"Include a clear call-to-action for MSME Business Loans & Personal Loans and relevant hashtags."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"thinkingConfig": {"thinkingLevel": "minimal"}}
    }
    
    try:
        res = requests.post(url, json=payload, timeout=25)
        data = res.json()
        if res.ok and "candidates" in data:
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
            return {"status": "success", "generated_caption": text}
        raise HTTPException(status_code=500, detail=data.get("error", {}).get("message", "Generation error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publish-to-socials")
def publish_to_socials(request: PublishRequest):
    if not META_SYSTEM_TOKEN:
        raise HTTPException(status_code=500, detail="META_SYSTEM_TOKEN is missing in environment variables.")
    
    target_page_id = request.page_id or DEFAULT_FB_PAGE_ID
    
    try:
        accounts_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={META_SYSTEM_TOKEN}"
        acc_res = requests.get(accounts_url, timeout=15)
        acc_data = acc_res.json()
        
        page_access_token = META_SYSTEM_TOKEN
        if "data" in acc_data:
            for page in acc_data["data"]:
                if page.get("id") == target_page_id:
                    page_access_token = page.get("access_token")
                    break

        fb_url = f"https://graph.facebook.0/v18.0/{target_page_id}/feed".replace(".0", "")
        fb_payload = {
            "message": request.message,
            "access_token": page_access_token
        }
        fb_response = requests.post(fb_url, data=fb_payload, timeout=30)
        fb_data = fb_response.json()

        if "error" in fb_data:
            error_msg = fb_data["error"].get("message", str(fb_data["error"]))
            raise HTTPException(status_code=400, detail=f"Facebook API Error: {error_msg}")

        return {
            "status": "completed",
            "publishing_results": {"facebook": fb_data}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
