from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard")
async def dashboard(request: Request):
    """Show user dashboard"""
    # Check if user is logged in
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    # You can add token balance here later
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_email": user_email
    })