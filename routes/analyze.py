from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

print(f"🔍 Templates folder: {os.path.abspath('templates')}")
print(f"🔍 Looking for: {os.path.abspath(os.path.join('templates', 'docudecipher_home.html'))}")
print(f"🔍 File exists? {os.path.exists(os.path.join('templates', 'docudecipher_home.html'))}")

@router.get("/analyze")
async def analyze_home(request: Request):
    """Show feature selection page"""
    # Check if user is logged in
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse("docudecipher_home.html", {
        "request": request,
        "user_email": user_email
    })

@router.get("/docudecipher-home")
async def redirect_old_home():
    """Redirect old URL to new one"""
    return RedirectResponse("/analyze", status_code=301)  # 301 = permanent redirect