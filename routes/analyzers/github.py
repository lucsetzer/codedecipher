from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid
import asyncio
from shared.file_queue import save_analysis
from routes.analyzers.base import run_analysis

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/analyze/github")
async def github_form(request: Request):
    """Show GitHub analysis form"""
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse("github_analyzer.html", {
        "request": request,
        "feature": "GitHub"
    })

@router.post("/process-github")
async def process_github(
    request: Request,
    repo_url: str = Form(...),
    branch: str = Form("main"),
    include_patterns: str = Form("*.py,*.js,*.json,*.md,*.yml"),
    specific_questions: str = Form(""),
    level: str = Form("professional"),
    doc_type: str = Form("github")
):
    """Process GitHub repository analysis"""
    
    # 1. Get user email FIRST
    user_email = request.session.get("user_email")
    is_demo = False
    
    # If not logged in, set up demo user
    if not user_email:
        client_ip = request.client.host
        user_email = f"demo_{client_ip}"
        is_demo = True
        print(f"🎁 Demo mode for IP: {client_ip}")
    
    # 2. CHECK TOKENS - RIGHT HERE
    from shared.auth import get_user_tokens
    if await get_user_tokens(user_email) <= 0:
        return RedirectResponse("/insufficient-tokens", status_code=303)
    
    # 3. NOW create analysis_id and proceed
    analysis_id = str(uuid.uuid4())
    
    # Build prompt
    prompt = f"""Analyze this GitHub repository for a {level} audience.

Repository: {repo_url}
Branch: {branch}
Include patterns: {include_patterns}

Please provide:
1. PROJECT OVERVIEW: What does this codebase do?
2. TECH STACK: Languages, frameworks, key dependencies
3. ARCHITECTURE: Main components and how they connect
4. COMPLEXITY: Areas that need attention
5. ONBOARDING: What a new developer needs to know

{specific_questions}"""
    
    # Store initial data
    data = {
        "user_email": request.session.get("user_email"),
        "feature": "github",
        "repo_url": repo_url,
        "branch": branch,
        "include_patterns": include_patterns,
        "specific_questions": specific_questions,
        "level": level,
        "status": "processing",
        "progress": 0.1,
        "message": "Cloning repository...",
        "created_at": asyncio.get_event_loop().time()
    }
    
    from shared.auth import get_user_tokens, deduct_token

    # Get user email from session (assuming you have this)
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse(url="/login", status_code=303)

    # Check tokens
    if await get_user_tokens(user_email) <= 0:
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
    return RedirectResponse(url=f"/github-loading/{analysis_id}", status_code=303)

@router.get("/github-loading/{analysis_id}")
async def github_loading(analysis_id: str, request: Request):
    """Show loading page for GitHub analysis"""
    from shared.file_queue import load_analysis
    
    data = load_analysis(analysis_id)
    
    if not data:
        return RedirectResponse(url="/analyze/github", status_code=303)
    
    if data.get("status") == "complete":
        return RedirectResponse(url=f"/result/{analysis_id}", status_code=303)
    
    # Show loading template with feature name
    print(f"📂 Looking for template: loading.html")
    
    return templates.TemplateResponse("loading.html", {
        "request": request,
        "feature": "GitHub Repository",
        "analysis_id": analysis_id
    })
