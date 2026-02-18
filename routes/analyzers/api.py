from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid
import asyncio
from shared.file_queue import save_analysis
from routes.analyzers.base import run_analysis
from starlette.middleware.sessions import SessionMiddleware
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/analyze/api")
async def api_form(request: Request):
    """Show API documentation analysis form"""
    # Check if user is logged in
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse("api_analyzer.html", {
        "request": request,
        "feature": "API"
    })

@router.post("/process-api")
async def process_api(
    request: Request,
    api_url: str = Form(...),
    api_type: str = Form("rest"),
    specific_questions: str = Form(""),
    level: str = Form("professional")
):
    """Process API documentation analysis"""
    
    analysis_id = str(uuid.uuid4())
    
    # Build prompt
    prompt = f"""Analyze this API documentation for a {level} audience.

API URL: {api_url}
API Type: {api_type}

Please provide:
1. PURPOSE: What does this API do?
2. ENDPOINTS: Key operations and their purpose
3. AUTH: How authentication works
4. DATA FORMATS: Request/response structure
5. USAGE: Common implementation patterns

{specific_questions}"""
    
    # Store initial data
    data = {
        "feature": "api",
        "api_url": api_url,
        "api_type": api_type,
        "specific_questions": specific_questions,
        "level": level,
        "status": "processing",
        "progress": 0.1,
        "message": "Fetching API documentation...",
        "created_at": asyncio.get_event_loop().time()
    }
    
    from shared.auth import get_user_tokens, deduct_token

    # Get user email from session (assuming you have this)
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse(url="/login", status_code=303)

    # Check tokens
    if get_user_tokens(user_email) <= 0:
        return RedirectResponse(url="/insufficient-tokens", status_code=303)

    # ... rest of analysis code ...

    # After successful completion, deduct token
    if data["status"] == "complete":
        deduct_token(user_email)

    # Save to queue
    save_analysis(analysis_id, data)
    
    # Start background task
    asyncio.create_task(run_analysis(analysis_id, data, prompt))
    
    # Redirect to loading
    return RedirectResponse(url=f"/api-loading/{analysis_id}", status_code=303)

@router.get("/api-loading/{analysis_id}")
async def api_loading(analysis_id: str, request: Request):
    """Show loading page for API analysis"""
    from shared.file_queue import load_analysis
    
    data = load_analysis(analysis_id)
    
    if not data:
        return RedirectResponse(url="/analyze/api", status_code=303)
    
    if data.get("status") == "complete":
        return RedirectResponse(url=f"/result/{analysis_id}", status_code=303)
    
    # Show loading template with feature name
    return templates.TemplateResponse("loading.html", {
        "request": request,
        "feature": "API Documentation",
        "analysis_id": analysis_id
    })