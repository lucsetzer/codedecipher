from routes.analyzers.base import run_analysis
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from shared.file_queue import save_analysis
from fastapi.templating import Jinja2Templates

import uuid
import asyncio

templates = Jinja2Templates(directory="templates")

print("✅ SNIPPET ROUTER IS LOADING")
print(f"🔍 Current file: {__file__}")

router = APIRouter()

@router.get("/analyze/snippet")
async def snippet_form(request: Request):
    """Show the snippet analysis form"""
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("snippet_analyzer.html", {"request": request})

@router.post("/process-snippet")
async def process_snippet(
    request: Request,
    code: str = Form(...),
    language: str = Form("auto"),
    level: str = Form("professional"),
    specific_questions: str = Form(""),
    doc_type: str = Form("functions")
):
    """Process code snippet analysis"""
    
    analysis_id = str(uuid.uuid4())
    
    # Build prompt
    prompt = f"""Analyze this code for a {level} audience:

{code}

Focus on:
1. PURPOSE: What does this code do?
2. LOGIC: Key operations and flow
3. COMPLEXITY: Areas that need attention
4. EDGE CASES: Missing error handling
5. IMPROVEMENTS: How to make it better"""

    if specific_questions:
        prompt += f"\n\nSpecific questions: {specific_questions}"
    
    # Store initial data
    data = {
        "user_email": request.session.get("user_email"),
        "feature": "snippet",
        "code": code[:500],
        "language": language,
        "level": level,
        "specific_questions": specific_questions,
        "status": "processing",
        "progress": 0.1,
        "message": "Starting analysis...",
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

    # After successful completion, deduct token
    if data["status"] == "complete":
        deduct_token(user_email)

    # Save initial state
    from shared.file_queue import save_analysis
    save_analysis(analysis_id, data)
    
    # Start background task using shared base
    asyncio.create_task(run_analysis(analysis_id, data, prompt))
    
    # Redirect to loading
    return RedirectResponse(url=f"/snippet-loading/{analysis_id}", status_code=303)

@router.get("/snippet-loading/{analysis_id}")
async def snippet_loading(analysis_id: str, request: Request):
    """Show loading page for snippet analysis"""
    from shared.file_queue import load_analysis
    
    data = load_analysis(analysis_id)
    
    if not data:
        return RedirectResponse(url="/analyze/snippet", status_code=303)
    
    if data.get("status") == "complete":
        return RedirectResponse(url=f"/result/{analysis_id}", status_code=303)
    
    # Use the shared loading template with spinner
    return templates.TemplateResponse("loading.html", {
        "request": request,
        "feature": "Code Snippet",
        "analysis_id": analysis_id
    })
