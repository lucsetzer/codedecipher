from routes.analyzers.base import run_analysis
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from shared.file_queue import save_analysis

import uuid
import asyncio

router = APIRouter()
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
    
    # Save initial state
    from shared.file_queue import save_analysis
    save_analysis(analysis_id, data)
    
    # Start background task using shared base
    asyncio.create_task(run_analysis(analysis_id, data, prompt))
    
    # Redirect to loading
    return RedirectResponse(url=f"/snippet-loading/{analysis_id}", status_code=303)