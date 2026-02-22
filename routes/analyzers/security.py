from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import uuid
import shutil
import tempfile
import asyncio
from shared.file_queue import save_analysis
from routes.analyzers.base import run_analysis
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/analyze/security")
async def security_form(request: Request):
    """Show security analysis form"""
    return templates.TemplateResponse("security_analyzer.html", {
        "request": request,
        "feature": "Security"
    })

@router.post("/process-security")
async def process_security(
    request: Request,
    code: str = Form(None),
    file: UploadFile = File(None),
    repo_url: str = Form(None),
    scan_type: str = Form("full"),
    threshold: str = Form("medium"),
    specific_questions: str = Form(""),
    level: str = Form("professional")
):
    """Process security analysis"""
    
    analysis_id = str(uuid.uuid4())
    
    # Handle file upload if present
    content = code or ""
    if file and file.filename:
        content = (await file.read()).decode()[:10000]
    
    # Build prompt (use your existing security prompt)
    prompt = f"""Perform a security review of this code for a {level} audience.

Scan type: {scan_type}
Threshold: {threshold}

CODE TO ANALYZE:
{content}

{specific_questions}

Please provide:
1. VULNERABILITIES: Specific security issues found
2. INPUT VALIDATION: How user input is handled
3. AUTH/PERMISSIONS: Access control concerns
4. SECURE CODING: Best practices to implement
5. PRIORITY: What to fix immediately"""
    
    # Store initial data
    data = {
        "feature": "security",
        "code": content[:500],
        "scan_type": scan_type,
        "threshold": threshold,
        "specific_questions": specific_questions,
        "level": level,
        "status": "processing",
        "progress": 0.1,
        "message": "Starting security scan...",
        "created_at": asyncio.get_event_loop().time()
    }
    
    # Save to queue
    save_analysis(analysis_id, data)
    
    # Start background task
    asyncio.create_task(run_analysis(analysis_id, data, prompt))
    
    # Redirect to loading
    return RedirectResponse(url=f"/security-loading/{analysis_id}", status_code=303)

@router.get("/security-loading/{analysis_id}")
async def security_loading(analysis_id: str, request: Request):
    """Show loading page for security analysis"""
    from shared.file_queue import load_analysis
    
    data = load_analysis(analysis_id)
    
    if not data:
        return RedirectResponse(url="/analyze/security", status_code=303)
    
    if data.get("status") == "complete":
        return RedirectResponse(url=f"/result/{analysis_id}", status_code=303)
    
    # Show loading template with feature name
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse("loading.html", {
        "request": request,
        "feature": "Security Scan",
        "analysis_id": analysis_id
    })

@router.post("/process-github-security")
async def process_github_security(
    request: Request,
    repo_url: str = Form(...),
    scan_type: str = Form("full"),
    severity: str = Form("high"),
    level: str = Form("professional")
):
    """Process security scan of a GitHub repository"""
    
    analysis_id = str(uuid.uuid4())
    
    prompt = f"""Perform a security review of this GitHub repository for a {level} audience.

Repository: {repo_url}
Scan type: {scan_type}
Minimum severity: {severity}

Please provide:
1. VULNERABILITIES: Specific security issues found
2. SECRETS: Hardcoded credentials, API keys
3. DEPENDENCIES: Vulnerable packages
4. CODE QUALITY: Security anti-patterns
5. PRIORITY: What to fix immediately"""
    
    data = {
        "feature": "security",
        "repo_url": repo_url,
        "scan_type": scan_type,
        "severity": severity,
        "level": level,
        "status": "processing",
        "progress": 0.1,
        "message": "Cloning repository for security scan...",
        "created_at": asyncio.get_event_loop().time()
    }
    
    from shared.file_queue import save_analysis
    save_analysis(analysis_id, data)
    
    from routes.analyzers.base import run_analysis
    asyncio.create_task(run_analysis(analysis_id, data, prompt))
    
    return RedirectResponse(url=f"/security-loading/{analysis_id}", status_code=303)

@router.post("/process-security-upload")
async def process_security_upload(
    request: Request,
    file: UploadFile = File(...),
    scan_type: str = Form("full"),
    severity: str = Form("high"),
    level: str = Form("professional")
):
    """Process security scan from uploaded file"""
    
    # Check login
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    # Check tokens
    from shared.auth import get_user_tokens, deduct_token
    if get_user_tokens(user_email) <= 0:
        return RedirectResponse("/insufficient-tokens", status_code=303)
    
    analysis_id = str(uuid.uuid4())
    
    # Read file content
    content = await file.read()
    try:
        code = content.decode()[:10000]
    except:
        code = "[Binary file content could not be decoded]"
    
    prompt = f"""Perform a security review of this code for a {level} audience.
Filename: {file.filename}
Scan type: {scan_type}
Minimum severity: {severity}
CODE TO ANALYZE:
{code}
Please provide security analysis focusing on vulnerabilities, secrets, and issues."""
    
    # Store initial data WITH user_email
    data = {
        "feature": "security",
        "filename": file.filename,
        "code": code[:500],
        "scan_type": scan_type,
        "severity": severity,
        "level": level,
        "user_email": user_email,  # ← CRITICAL
        "status": "processing",
        "progress": 0.1,
        "message": "Scanning uploaded file...",
        "created_at": asyncio.get_event_loop().time()
    }
    
    # Save and start background task
    from shared.file_queue import save_analysis
    save_analysis(analysis_id, data)
    
    from routes.analyzers.base import run_analysis
    asyncio.create_task(run_analysis(analysis_id, data, prompt))
    
    return RedirectResponse(url=f"/security-loading/{analysis_id}", status_code=303)
    
    asyncio.create_task(delete_later())
